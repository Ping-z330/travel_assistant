<script setup lang="ts">
import type { TripPlan } from '../../types/trip'

defineProps<{
  tripPlan: TripPlan
}>()
</script>

<template>
  <section class="hero-summary">
    <div>
      <p class="eyebrow">Generated Trip Plan</p>
      <h1>{{ tripPlan.city }}旅行计划</h1>
      <p class="summary-text">{{ tripPlan.overall_suggestion }}</p>
    </div>

    <div class="summary-meta">
      <span>出发日期</span>
      <strong>{{ tripPlan.start_date }}</strong>
      <span>行程天数</span>
      <strong>{{ tripPlan.days.length }} 天</strong>
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

.hero-summary {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 28px;
  align-items: end;
  padding: 34px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.hero-summary h1 {
  margin: 0 0 12px;
  color: var(--text);
  font-size: clamp(34px, 5vw, 54px);
  line-height: 1.08;
}

.summary-text {
  max-width: 720px;
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.summary-meta {
  display: grid;
  gap: 8px;
  padding: 18px;
  background: var(--soft);
  border: 1px solid #d3e2d8;
  border-radius: 8px;
}

.summary-meta span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.summary-meta strong {
  color: var(--primary-dark);
  font-size: 18px;
}

@media (max-width: 860px) {
  .hero-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .hero-summary {
    padding: 20px;
  }
}
</style>
