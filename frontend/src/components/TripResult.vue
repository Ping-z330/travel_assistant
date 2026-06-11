<script setup lang="ts">
import { computed, ref } from 'vue'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { useRouter } from 'vue-router'
import type { DayPlan, TripPlan } from '../types/trip'
import BudgetSummary from './result/BudgetSummary.vue'
import DayPlanCard from './result/DayPlanCard.vue'
import ResultSidebar from './result/ResultSidebar.vue'
import TravelMapPreview from './result/TravelMapPreview.vue'
import TripOverview from './result/TripOverview.vue'

const props = defineProps<{
  tripPlan: TripPlan
}>()

const router = useRouter()
const activeSection = ref<'overview' | number>('overview')
const exportRef = ref<HTMLElement | null>(null)
const exporting = ref(false)

const visibleDays = computed(() => {
  if (activeSection.value === 'overview') {
    return []
  }

  return props.tripPlan.days.filter((day: DayPlan) => day.day === activeSection.value)
})

const backToForm = () => {
  router.push('/')
}

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

    pdf.save(`${props.tripPlan.city}-旅行计划.pdf`)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <section class="trip-result">
    <header class="result-nav">
      <div>
        <p class="nav-eyebrow">AI Travel Plan</p>
        <strong>{{ tripPlan.city }} {{ tripPlan.days.length }} 日旅行计划</strong>
        <span class="nav-meta">{{ tripPlan.start_date }} 出发</span>
      </div>

      <div class="result-actions">
        <button class="back-button" type="button" @click="backToForm">返回修改</button>
        <button class="export-button" type="button" :disabled="exporting" @click="exportToPdf">
          {{ exporting ? '正在整理 PDF...' : '导出 PDF' }}
        </button>
      </div>
    </header>

    <div ref="exportRef" class="export-surface">
      <main class="result-shell">
        <ResultSidebar
          :active-section="activeSection"
          :days="tripPlan.days"
          @select-section="activeSection = $event"
        />

        <div class="result-content">
          <template v-if="activeSection === 'overview'">
            <section class="overview-dashboard" aria-label="行程总览">
              <TripOverview :trip-plan="tripPlan" />
              <BudgetSummary :budget="tripPlan.budget" />
            </section>
            <section class="map-showcase" aria-label="路线地图">
              <TravelMapPreview :trip-plan="tripPlan" />
            </section>
          </template>

          <section v-else class="day-timeline" aria-label="每日行程">
            <DayPlanCard v-for="day in visibleDays" :key="day.day" :day="day" />
          </section>
        </div>
      </main>
    </div>
  </section>
</template>

<style scoped>
.trip-result {
  min-height: 100vh;
  padding: 28px 20px 56px;
  background:
    linear-gradient(180deg, rgba(23, 107, 93, 0.14), transparent 320px),
    var(--bg);
}

.result-nav {
  width: min(1240px, 100%);
  margin: 0 auto 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
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
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 800;
}

.result-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
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

.back-button {
  min-height: 42px;
  padding: 0 18px;
  color: var(--primary-dark);
  background: rgba(255, 255, 255, 0.78);
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

.export-button:disabled {
  opacity: 0.7;
  cursor: wait;
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
    padding: 18px 14px 38px;
  }

  .result-nav {
    display: grid;
    align-items: flex-start;
  }

  .result-actions {
    justify-content: flex-start;
  }
}
</style>
