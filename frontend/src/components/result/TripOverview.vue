<script setup lang="ts">
import type { TripPlan } from '../../types/trip'

defineProps<{
  tripPlan: TripPlan
}>()
</script>

<template>
  <section class="hero-summary">
    <div>
      <p class="eyebrow">Trip Brief</p>
      <h1>整体建议</h1>
      <div class="summary-meta">
        <div>
          <span>目的地</span>
          <strong>{{ tripPlan.city }}</strong>
        </div>
        <div>
          <span>出发日期</span>
          <strong>{{ tripPlan.start_date }}</strong>
        </div>
        <div>
          <span>行程天数</span>
          <strong>{{ tripPlan.days.length }} 天</strong>
        </div>
      </div>
      <p class="summary-text">{{ tripPlan.overall_suggestion }}</p>
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
  height: 100%;
  padding: 26px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.hero-summary h1 {
  margin: 0 0 12px;
  color: var(--text);
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.12;
}

.summary-text {
  max-width: 680px;
  margin: 18px 0 0;
  color: var(--muted);
  line-height: 1.7;
}

.summary-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 0;
  padding: 16px;
  background: var(--soft);
  border: 1px solid #d3e2d8;
  border-radius: 8px;
}

.summary-meta div {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.summary-meta span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.summary-meta strong {
  color: var(--primary-dark);
  font-size: 17px;
}

@media (max-width: 860px) {
}

@media (max-width: 560px) {
  .hero-summary {
    padding: 20px;
  }

  .summary-meta {
    grid-template-columns: 1fr;
  }
}
</style>
