<script setup lang="ts">
import type { TransportSummary } from '../../types/trip'

defineProps<{
  transportSummary: TransportSummary
}>()
</script>

<template>
  <section class="transport-card" aria-label="交通建议">
    <div class="transport-header">
      <div>
        <p class="eyebrow">Transport</p>
        <h2>交通推荐</h2>
      </div>
      <strong>{{ transportSummary.recommended_mode }}</strong>
    </div>

    <p class="transport-summary">{{ transportSummary.summary }}</p>

    <div class="transport-route">
      <span>{{ transportSummary.departure_city || '出发地未填' }}</span>
      <i></i>
      <span>{{ transportSummary.destination_city }}</span>
    </div>

    <div class="transport-options">
      <article
        v-for="option in transportSummary.options"
        :key="`${option.mode}-${option.title}`"
        class="transport-option"
      >
        <span class="option-mode">{{ option.mode }}</span>
        <strong>{{ option.title }}</strong>
        <p>{{ option.description }}</p>
        <em>{{ option.estimated_duration }} · {{ option.estimated_cost }}</em>
        <small>{{ option.booking_advice }}</small>
      </article>
    </div>
  </section>
</template>

<style scoped>
.transport-card {
  display: grid;
  gap: 16px;
  padding: 22px;
  background: linear-gradient(180deg, #fffaf1, #ffffff);
  border: 1px solid rgba(216, 139, 45, 0.24);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.transport-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--accent);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.transport-header h2 {
  margin: 0;
  color: var(--text);
  font-size: 24px;
  line-height: 1.15;
}

.transport-header strong {
  flex: 0 0 auto;
  color: var(--primary-dark);
  font-size: 18px;
  font-weight: 900;
}

.transport-summary {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.transport-route {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 12px 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.transport-route span {
  color: var(--primary-dark);
  font-size: 14px;
  font-weight: 900;
}

.transport-route i {
  flex: 1 1 160px;
  height: 2px;
  min-width: 70px;
  background: linear-gradient(90deg, rgba(23, 107, 93, 0.2), rgba(216, 139, 45, 0.7));
}

.transport-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.transport-option {
  display: grid;
  gap: 8px;
  padding: 14px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.option-mode {
  width: fit-content;
  padding: 4px 8px;
  color: var(--primary-dark);
  background: var(--soft);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.transport-option strong {
  color: var(--text);
  font-size: 16px;
}

.transport-option p {
  margin: 0;
  color: var(--muted);
  line-height: 1.65;
}

.transport-option em {
  color: var(--primary-dark);
  font-size: 13px;
  font-style: normal;
  font-weight: 900;
}

.transport-option small {
  color: var(--muted);
  line-height: 1.6;
}

@media (max-width: 860px) {
  .transport-options {
    grid-template-columns: 1fr;
  }
}
</style>
