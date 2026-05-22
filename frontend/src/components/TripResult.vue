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
        <p class="nav-eyebrow">AI Travel Assistant</p>
        <strong>智能旅行助手</strong>
      </div>

      <div class="result-actions">
        <button class="export-button" type="button" :disabled="exporting" @click="exportToPdf">
          {{ exporting ? '导出中...' : '导出 PDF' }}
        </button>
        <button class="back-button" type="button" @click="backToForm">返回修改</button>
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
            <TripOverview :trip-plan="tripPlan" />
            <BudgetSummary :budget="tripPlan.budget" />
            <TravelMapPreview :trip-plan="tripPlan" />
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
    linear-gradient(180deg, rgba(23, 107, 93, 0.1), transparent 280px),
    var(--bg);
}

.result-nav {
  width: min(1120px, 100%);
  margin: 0 auto 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.result-nav strong {
  color: var(--text);
  font-size: 30px;
}

.nav-eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.result-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.result-shell {
  width: min(1120px, 100%);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 24px;
}

.result-content {
  display: grid;
  gap: 24px;
  min-width: 0;
}

.back-button {
  min-height: 42px;
  padding: 0 18px;
  color: #ffffff;
  background: var(--primary);
  border: 0;
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
}

.export-button {
  min-height: 42px;
  padding: 0 18px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid var(--line);
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
}

@media (max-width: 560px) {
  .trip-result {
    padding: 18px 14px 38px;
  }

  .result-nav {
    align-items: flex-start;
  }
}
</style>
