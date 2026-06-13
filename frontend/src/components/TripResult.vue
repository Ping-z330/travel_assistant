<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { useRouter } from 'vue-router'
import type { DayPlan, TripPlan } from '../types/trip'
import BudgetSummary from './result/BudgetSummary.vue'
import DayPlanCard from './result/DayPlanCard.vue'
import ResultSidebar from './result/ResultSidebar.vue'
import TravelMapPreview from './result/TravelMapPreview.vue'
import TransportSummaryCard from './result/TransportSummaryCard.vue'
import TripOverview from './result/TripOverview.vue'
import { saveTripPlanToHistory } from '../services/tripHistory'

const props = defineProps<{
  tripPlan: TripPlan
  savedTripId?: string | null
}>()

const emit = defineEmits<{
  updateTripPlan: [tripPlan: TripPlan]
  updateSavedTripId: [id: string]
}>()

const router = useRouter()
const activeSection = ref<'overview' | number>('overview')
const exportRef = ref<HTMLElement | null>(null)
const exporting = ref(false)
const isEditing = ref(false)
const draftPlan = ref<TripPlan | null>(null)
const saveStatus = ref<'idle' | 'saved' | 'dirty'>(props.savedTripId ? 'saved' : 'idle')

const cloneTripPlan = (tripPlan: TripPlan): TripPlan => JSON.parse(JSON.stringify(tripPlan))

const recalculateBudget = (tripPlan: TripPlan) => {
  const totalAttractions = tripPlan.days.reduce(
    (total, day) =>
      total +
      day.attractions.reduce((dayTotal, attraction) => dayTotal + Number(attraction.ticket_price || 0), 0),
    0,
  )
  const totalHotels = tripPlan.days.reduce(
    (total, day) => total + Number(day.hotel.price || 0),
    0,
  )

  tripPlan.budget.total_attractions = totalAttractions
  tripPlan.budget.total_hotels = totalHotels
  tripPlan.budget.total =
    totalAttractions +
    totalHotels +
    tripPlan.budget.total_meals +
    tripPlan.budget.total_transportation
}

const activeTripPlan = computed(() => draftPlan.value ?? props.tripPlan)

watch(
  () => props.savedTripId,
  (id) => {
    saveStatus.value = id ? 'saved' : 'idle'
  },
)

const visibleDays = computed(() => {
  if (activeSection.value === 'overview') {
    return []
  }

  return activeTripPlan.value.days.filter((day: DayPlan) => day.day === activeSection.value)
})

const backToForm = () => {
  router.push('/plan')
}

const startEditing = () => {
  draftPlan.value = cloneTripPlan(props.tripPlan)
  isEditing.value = true
}

const cancelEditing = () => {
  draftPlan.value = null
  isEditing.value = false
}

const saveEditing = () => {
  if (!draftPlan.value) {
    return
  }

  recalculateBudget(draftPlan.value)
  emit('updateTripPlan', cloneTripPlan(draftPlan.value))
  draftPlan.value = null
  isEditing.value = false
  saveStatus.value = props.savedTripId ? 'dirty' : 'idle'
}

const saveToHistory = () => {
  const savedTrip = saveTripPlanToHistory(activeTripPlan.value, {
    existingId: props.savedTripId,
  })
  emit('updateSavedTripId', savedTrip.id)
  saveStatus.value = 'saved'
}

const historyButtonLabel = computed(() => {
  if (saveStatus.value === 'dirty') {
    return '保存更新到我的行程'
  }

  if (saveStatus.value === 'saved') {
    return '已保存到我的行程'
  }

  return '保存到我的行程'
})

const exportToPdf = async () => {
  if (!exportRef.value || exporting.value) {
    return
  }

  exporting.value = true

  try {
    const canvas = await html2canvas(exportRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      windowWidth: exportRef.value.scrollWidth,
      windowHeight: exportRef.value.scrollHeight,
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')

    const pdfWidth = 210
    const pdfHeight = 297
    const margin = 10
    const contentWidth = pdfWidth - margin * 2
    const imgWidth = contentWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = margin

    pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight)
    heightLeft -= pdfHeight - margin * 2

    while (heightLeft > 0) {
      position = heightLeft - imgHeight + margin
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', margin, position, imgWidth, imgHeight)
      heightLeft -= pdfHeight - margin * 2
    }

    pdf.save(`${activeTripPlan.value.city}-旅行计划.pdf`)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <section class="trip-result">
    <header class="result-nav">
      <div class="result-title">
        <p class="nav-eyebrow">AI Travel Plan</p>
        <strong>{{ activeTripPlan.city }} {{ activeTripPlan.days.length }} 日旅行计划</strong>
        <span class="nav-meta">
          {{ activeTripPlan.start_date }} 出发
          <em v-if="props.savedTripId">{{ saveStatus === 'dirty' ? '历史行程 · 有未保存修改' : '历史行程 · 已同步' }}</em>
        </span>
      </div>

      <div class="result-actions">
        <div class="action-group">
          <button class="back-button" type="button" @click="backToForm">返回修改</button>
          <button
            v-if="!isEditing"
            class="edit-button"
            type="button"
            @click="startEditing"
          >
            编辑行程
          </button>
          <template v-else>
            <button class="back-button" type="button" @click="cancelEditing">取消编辑</button>
            <button class="save-button" type="button" @click="saveEditing">保存修改</button>
          </template>
        </div>

        <div class="action-group action-group--primary">
          <button v-if="!isEditing" class="history-button" type="button" @click="saveToHistory">
            {{ historyButtonLabel }}
          </button>
          <button class="export-button" type="button" :disabled="exporting" @click="exportToPdf">
            {{ exporting ? '正在整理 PDF...' : '导出 PDF' }}
          </button>
        </div>
      </div>
    </header>

    <div ref="exportRef" class="export-surface">
      <main class="result-shell">
        <ResultSidebar
          :active-section="activeSection"
          :days="activeTripPlan.days"
          @select-section="activeSection = $event"
        />

        <div class="result-content">
          <template v-if="activeSection === 'overview'">
            <div v-if="isEditing" class="edit-banner">
              <strong>正在编辑当前行程</strong>
              <span>保存后会更新概览、地图和 PDF 导出内容。</span>
            </div>
            <section class="overview-dashboard" aria-label="行程总览">
              <TripOverview :trip-plan="activeTripPlan" />
              <BudgetSummary :budget="activeTripPlan.budget" />
            </section>
            <section
              v-if="activeTripPlan.transport_summary"
              class="transport-showcase"
              aria-label="交通建议"
            >
              <TransportSummaryCard :transport-summary="activeTripPlan.transport_summary" />
            </section>
            <section class="map-showcase" aria-label="路线地图">
              <TravelMapPreview :trip-plan="activeTripPlan" />
            </section>
          </template>

          <section v-else class="day-timeline" aria-label="每日行程">
            <DayPlanCard
              v-for="day in visibleDays"
              :key="day.day"
              :day="day"
              :editing="isEditing"
            />
          </section>
        </div>
      </main>
    </div>
  </section>
</template>

<style scoped>
.trip-result {
  min-height: calc(100vh - 68px);
  padding: 44px 20px 56px;
  background:
    linear-gradient(180deg, rgba(23, 107, 93, 0.14), transparent 320px),
    var(--bg);
}

.result-nav {
  width: min(1240px, 100%);
  margin: 0 auto 28px;
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(23, 107, 93, 0.12);
  border-radius: 8px;
  box-shadow: 0 18px 44px rgba(31, 48, 39, 0.1);
  backdrop-filter: blur(12px);
}

.result-title {
  display: grid;
  align-content: center;
  min-width: 260px;
}

.result-nav strong {
  display: block;
  color: var(--text);
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.12;
}

.nav-eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.nav-meta {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 800;
}

.nav-meta em {
  padding: 3px 8px;
  color: var(--primary-dark);
  background: var(--soft);
  border: 1px solid rgba(23, 107, 93, 0.12);
  border-radius: 999px;
  font-size: 12px;
  font-style: normal;
}

.result-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-content: center;
  align-items: center;
  justify-content: flex-end;
  min-width: min(100%, 440px);
}

.action-group {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  padding: 4px;
  background: rgba(23, 107, 93, 0.045);
  border: 1px solid rgba(23, 107, 93, 0.08);
  border-radius: 8px;
}

.action-group--primary {
  background: transparent;
  border-color: transparent;
}

.result-shell {
  width: min(1240px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 208px minmax(0, 1fr);
  gap: 24px;
}

.result-content {
  display: grid;
  gap: 18px;
  min-width: 0;
}

.overview-dashboard {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 420px);
  gap: 18px;
  align-items: stretch;
}

.map-showcase {
  min-width: 0;
}

.transport-showcase {
  min-width: 0;
}

.back-button {
  min-height: 42px;
  padding: 0 18px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
}

.export-button {
  min-height: 42px;
  padding: 0 18px;
  color: #ffffff;
  background: var(--primary);
  border: 1px solid var(--primary);
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
}

.edit-button,
.save-button,
.history-button {
  min-height: 42px;
  padding: 0 18px;
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
}

.edit-button {
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid var(--line);
}

.save-button {
  color: #ffffff;
  background: var(--accent);
  border: 1px solid var(--accent);
}

.history-button {
  color: var(--primary-dark);
  background: #edf5ef;
  border: 1px solid rgba(23, 107, 93, 0.18);
}

.export-button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.edit-banner {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  color: var(--primary-dark);
  background: #fff8ec;
  border: 1px solid rgba(216, 139, 45, 0.26);
  border-radius: 8px;
}

.edit-banner strong,
.edit-banner span {
  font-size: 13px;
}

.edit-banner span {
  color: var(--muted);
}

.day-timeline {
  display: grid;
  gap: 18px;
}

@media (max-width: 860px) {
  .result-shell {
    grid-template-columns: 1fr;
  }

  .overview-dashboard {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .trip-result {
    padding: 24px 14px 38px;
  }

  .result-nav {
    display: grid;
    align-items: flex-start;
  }

  .result-actions {
    min-width: 0;
    justify-content: flex-start;
  }

  .action-group {
    justify-content: flex-start;
  }

  .edit-banner {
    display: grid;
  }
}
</style>
