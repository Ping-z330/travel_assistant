<script setup lang="ts">
import { computed, ref } from 'vue'
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

const visibleDays = computed(() => {
  if (activeSection.value === 'overview') {
    return []
  }

  return props.tripPlan.days.filter((day: DayPlan) => day.day === activeSection.value)
})

const backToForm = () => {
  router.push('/')
}
</script>

<template>
  <section class="trip-result">
    <header class="result-nav">
      <div>
        <p class="nav-eyebrow">AI Travel Assistant</p>
        <strong>智能旅游助手</strong>
      </div>
      <button class="back-button" type="button" @click="backToForm">返回修改</button>
    </header>

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
