<script setup lang="ts">
import AMapLoader from '@amap/amap-jsapi-loader'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import type { TripPlan } from '../../types/trip'

const props = defineProps<{
  tripPlan: TripPlan
}>()

const mapContainerRef = ref<HTMLElement | null>(null)
const isMapReady = ref(false)
const mapError = ref('')

let mapInstance: any = null
let overlayInstances: any[] = []

const DAY_COLORS = ['#176b5d', '#d97706', '#2563eb', '#dc2626', '#7c3aed']
const HOTEL_COLOR = '#c27c2c'

const attractionCount = computed(() =>
  props.tripPlan.days.reduce((total, day) => total + day.attractions.length, 0),
)

const hotelCount = computed(() =>
  props.tripPlan.days.filter((day) => day.hotel.location).length,
)

const dayRoutes = computed(() =>
  props.tripPlan.days.map((day, index) => ({
    day: day.day,
    color: DAY_COLORS[index % DAY_COLORS.length],
    points: day.attractions.map((attraction, pointIndex) => ({
      day: day.day,
      order: pointIndex + 1,
      name: attraction.name,
      address: attraction.address,
      longitude: attraction.location.longitude,
      latitude: attraction.location.latitude,
      color: DAY_COLORS[index % DAY_COLORS.length],
    })),
  })),
)

const attractionPoints = computed(() => dayRoutes.value.flatMap((route) => route.points))

const hotelPoints = computed(() =>
  props.tripPlan.days
    .filter((day) => day.hotel.location)
    .map((day) => ({
      day: day.day,
      name: day.hotel.name,
      address: day.hotel.address,
      price: day.hotel.price,
      longitude: day.hotel.location!.longitude,
      latitude: day.hotel.location!.latitude,
      color: HOTEL_COLOR,
    })),
)

const initializeMap = async () => {
  if (!mapContainerRef.value) {
    return
  }

  const apiKey = import.meta.env.VITE_AMAP_JSAPI_KEY
  if (!apiKey) {
    mapError.value = '未配置高德地图 Key，请检查 frontend/.env.local。'
    return
  }

  try {
    await AMapLoader.load({
      key: apiKey,
      version: '2.0',
      plugins: ['AMap.Scale', 'AMap.ToolBar'],
    })

    const AMap = (window as any).AMap
    if (!AMap) {
      throw new Error('高德地图对象未成功挂载')
    }

    const firstPoint = attractionPoints.value[0] ?? hotelPoints.value[0]
    mapInstance = new AMap.Map(mapContainerRef.value, {
      zoom: 11,
      center: firstPoint
        ? [firstPoint.longitude, firstPoint.latitude]
        : [116.397128, 39.916527],
      viewMode: '3D',
      mapStyle: 'amap://styles/whitesmoke',
    })

    mapInstance.addControl(new AMap.Scale())
    mapInstance.addControl(new AMap.ToolBar())

    isMapReady.value = true
    renderMapOverlays()
  } catch (error) {
    mapError.value = error instanceof Error ? error.message : '高德地图加载失败'
  }
}

const clearMapOverlays = () => {
  if (!mapInstance || overlayInstances.length === 0) {
    overlayInstances = []
    return
  }

  mapInstance.remove(overlayInstances)
  overlayInstances = []
}

const renderMapOverlays = () => {
  if (!mapInstance || !(window as any).AMap) {
    return
  }

  clearMapOverlays()

  const AMap = (window as any).AMap
  const overlays: any[] = []

  dayRoutes.value.forEach((route) => {
    const routeMarkers = route.points.map((point) => {
      const marker = new AMap.Marker({
        position: [point.longitude, point.latitude],
        title: point.name,
        offset: new AMap.Pixel(-34, -18),
        content: `
          <div style="
            min-width: 68px;
            height: 36px;
            padding: 0 12px;
            border-radius: 999px;
            background: ${point.color};
            color: #ffffff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 800;
            border: 3px solid #ffffff;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
            white-space: nowrap;
          ">
            <span style="opacity: 0.82;">D${point.day}</span>
            <span style="width: 4px; height: 4px; border-radius: 999px; background: rgba(255,255,255,0.78);"></span>
            <span>${point.order}</span>
          </div>
        `,
      })

      const infoWindow = new AMap.InfoWindow({
        content: `
          <div style="padding: 8px 10px; min-width: 220px; line-height: 1.7;">
            <strong>${point.name}</strong><br/>
            <span style="color: ${point.color}; font-weight: 700;">第${point.day}天第${point.order}站</span><br/>
            <span>${point.address}</span>
          </div>
        `,
        offset: new AMap.Pixel(0, -24),
      })

      marker.on('click', () => {
        infoWindow.open(mapInstance, [point.longitude, point.latitude])
      })

      return marker
    })

    const routeLine = new AMap.Polyline({
      path: route.points.map((point) => [point.longitude, point.latitude]),
      strokeColor: route.color,
      strokeWeight: 5,
      strokeOpacity: 0.92,
      lineJoin: 'round',
      lineCap: 'round',
      showDir: true,
    })

    overlays.push(...routeMarkers, routeLine)
  })

  hotelPoints.value.forEach((hotel) => {
    const marker = new AMap.Marker({
      position: [hotel.longitude, hotel.latitude],
      title: hotel.name,
      offset: new AMap.Pixel(-18, -44),
      content: `
        <div style="
          width: 40px;
          height: 48px;
          display: grid;
          justify-items: center;
          align-items: start;
        ">
          <div style="
            width: 36px;
            height: 36px;
            border-radius: 12px 12px 12px 4px;
            background: ${hotel.color};
            color: #ffffff;
            display: grid;
            place-items: center;
            font-size: 16px;
            font-weight: 900;
            border: 3px solid #ffffff;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
          ">
            住
          </div>
        </div>
      `,
    })

    const infoWindow = new AMap.InfoWindow({
      content: `
        <div style="padding: 8px 10px; min-width: 240px; line-height: 1.7;">
          <strong>${hotel.name}</strong><br/>
          <span style="color: ${hotel.color}; font-weight: 700;">第${hotel.day}天住宿点</span><br/>
          <span>${hotel.address}</span><br/>
          <span>参考价格：${hotel.price} 元</span>
        </div>
      `,
      offset: new AMap.Pixel(0, -26),
    })

    marker.on('click', () => {
      infoWindow.open(mapInstance, [hotel.longitude, hotel.latitude])
    })

    overlays.push(marker)
  })

  overlayInstances = overlays
  mapInstance.add(overlays)
  mapInstance.setFitView(overlays, false, [60, 60, 60, 60])
}

onMounted(() => {
  initializeMap()
})

watch(
  () => [dayRoutes.value, hotelPoints.value],
  () => {
    if (isMapReady.value) {
      renderMapOverlays()
    }
  },
  { deep: true },
)

onUnmounted(() => {
  clearMapOverlays()

  if (mapInstance) {
    mapInstance.destroy()
    mapInstance = null
  }
})
</script>

<template>
  <section class="travel-map-panel" aria-label="旅游地图">
    <div class="map-header">
      <div>
        <p class="eyebrow">Travel Map</p>
        <h2>旅游地图</h2>
      </div>
      <span>{{ isMapReady ? '高德地图已连接' : '地图预览' }}</span>
    </div>

    <div ref="mapContainerRef" class="map-canvas">
      <div v-if="mapError" class="map-overlay-message map-overlay-message--error">
        {{ mapError }}
      </div>
      <div v-else-if="!isMapReady" class="map-overlay-message">地图加载中...</div>
    </div>

    <div class="map-summary">
      <div>
        <span>目的地</span>
        <strong>{{ tripPlan.city }}</strong>
      </div>
      <div>
        <span>景点数量</span>
        <strong>{{ attractionCount }} 个</strong>
      </div>
      <div>
        <span>住宿点位</span>
        <strong>{{ hotelCount }} 个</strong>
      </div>
    </div>

    <div class="map-legend" aria-label="路线图例">
      <div v-for="route in dayRoutes" :key="route.day" class="legend-item">
        <i class="legend-color" :style="{ backgroundColor: route.color }"></i>
        <span>第 {{ route.day }} 天路线</span>
      </div>
      <div class="legend-item legend-item--hotel">
        <i class="legend-color" :style="{ backgroundColor: HOTEL_COLOR }"></i>
        <span>住宿点位</span>
      </div>
    </div>

    <div class="map-point-section">
      <h3>景点点位</h3>
      <div class="map-point-list" aria-label="景点点位列表">
        <div
          v-for="point in attractionPoints"
          :key="`${point.day}-${point.order}-${point.name}`"
          class="map-point-item"
        >
          <i class="point-color" :style="{ backgroundColor: point.color }"></i>
          <span>第 {{ point.day }} 天</span>
          <strong>{{ point.name }}</strong>
          <em>{{ point.longitude }}, {{ point.latitude }}</em>
        </div>
      </div>
    </div>

    <div v-if="hotelPoints.length > 0" class="map-point-section">
      <h3>住宿点位</h3>
      <div class="map-point-list" aria-label="住宿点位列表">
        <div
          v-for="hotel in hotelPoints"
          :key="`${hotel.day}-${hotel.name}`"
          class="map-point-item"
        >
          <i class="point-color" :style="{ backgroundColor: hotel.color }"></i>
          <span>第 {{ hotel.day }} 天</span>
          <strong>{{ hotel.name }}</strong>
          <em>{{ hotel.longitude }}, {{ hotel.latitude }}</em>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.travel-map-panel {
  display: grid;
  gap: 18px;
  padding: 24px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.map-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
}

.map-header h2 {
  margin: 4px 0 0;
  color: var(--text);
  font-size: 26px;
}

.map-header > span {
  padding: 8px 12px;
  color: var(--primary-dark);
  background: var(--soft);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
}

.map-canvas {
  position: relative;
  min-height: 360px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(23, 107, 93, 0.06), rgba(23, 107, 93, 0.02));
}

.map-overlay-message {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  place-items: center;
  padding: 20px;
  color: var(--primary-dark);
  background: rgba(251, 252, 250, 0.88);
  text-align: center;
  font-weight: 700;
}

.map-overlay-message--error {
  color: #b42318;
  background: rgba(254, 243, 242, 0.96);
}

.map-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.map-summary div {
  display: grid;
  gap: 6px;
  padding: 14px;
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.map-summary span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.map-summary strong {
  color: var(--primary-dark);
}

.map-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--text);
  font-size: 13px;
  font-weight: 700;
}

.legend-item--hotel {
  background: #fff8ef;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex: 0 0 auto;
}

.map-point-section {
  display: grid;
  gap: 10px;
}

.map-point-section h3 {
  margin: 0;
  color: var(--text);
  font-size: 16px;
}

.map-point-list {
  display: grid;
  gap: 10px;
}

.map-point-item {
  display: grid;
  grid-template-columns: 16px 80px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.point-color {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

.map-point-item span {
  color: var(--accent);
  font-size: 13px;
  font-weight: 800;
}

.map-point-item strong {
  color: var(--text);
}

.map-point-item em {
  color: var(--muted);
  font-size: 13px;
  font-style: normal;
}

@media (max-width: 860px) {
  .map-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .travel-map-panel {
    padding: 20px;
  }

  .map-header {
    display: grid;
  }

  .map-point-item {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
