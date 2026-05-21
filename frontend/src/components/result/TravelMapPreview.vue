<script setup lang="ts">
import { computed } from 'vue'
import type { TripPlan } from '../../types/trip'

const props = defineProps<{
  tripPlan: TripPlan
}>()

const attractionCount = computed(() =>
  props.tripPlan.days.reduce((total, day) => total + day.attractions.length, 0),
)

const mapPoints = computed(() =>
  props.tripPlan.days.flatMap((day) =>
    day.attractions.map((attraction) => ({
      day: day.day,
      name: attraction.name,
      longitude: attraction.location.longitude,
      latitude: attraction.location.latitude,
    })),
  ),
)
</script>

<template>
  <section class="travel-map-panel" aria-label="旅游地图">
    <div class="map-header">
      <div>
        <p class="eyebrow">Travel Map</p>
        <h2>旅游地图</h2>
      </div>
      <span>高德地图预留区域</span>
    </div>

    <div class="map-canvas">
      <div class="map-route-line"></div>
      <span class="map-pin map-pin-start">1</span>
      <span class="map-pin map-pin-middle">2</span>
      <span class="map-pin map-pin-end">3</span>
      <p>后续将在这里接入高德地图，展示景点标记与路线。</p>
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
        <span>地图能力</span>
        <strong>POI / 标点 / 路线</strong>
      </div>
    </div>

    <div class="map-point-list" aria-label="地图点位列表">
      <div
        v-for="point in mapPoints"
        :key="`${point.day}-${point.name}`"
        class="map-point-item"
      >
        <span>第 {{ point.day }} 天</span>
        <strong>{{ point.name }}</strong>
        <em>{{ point.longitude }}, {{ point.latitude }}</em>
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
  display: grid;
  min-height: 320px;
  place-items: center;
  overflow: hidden;
  color: rgba(255, 255, 255, 0.86);
  background:
    linear-gradient(rgba(17, 79, 67, 0.58), rgba(17, 79, 67, 0.74)),
    repeating-linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.08) 0,
      rgba(255, 255, 255, 0.08) 1px,
      transparent 1px,
      transparent 28px
    ),
    #176b5d;
  border-radius: 8px;
}

.map-canvas p {
  position: relative;
  z-index: 2;
  width: min(420px, calc(100% - 48px));
  margin: 0;
  text-align: center;
  line-height: 1.8;
}

.map-route-line {
  position: absolute;
  inset: 30% 18% 34% 18%;
  border-top: 3px dashed rgba(255, 245, 223, 0.72);
  border-right: 3px dashed rgba(255, 245, 223, 0.72);
  border-radius: 50%;
  transform: rotate(-8deg);
}

.map-pin {
  position: absolute;
  z-index: 3;
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  color: var(--primary-dark);
  background: #fff5df;
  border: 3px solid #ffffff;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 900;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
}

.map-pin-start {
  top: 26%;
  left: 20%;
}

.map-pin-middle {
  top: 55%;
  left: 48%;
}

.map-pin-end {
  top: 32%;
  right: 20%;
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

.map-point-list {
  display: grid;
  gap: 10px;
}

.map-point-item {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 8px;
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
