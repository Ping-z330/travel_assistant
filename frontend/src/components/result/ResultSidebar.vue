<script setup lang="ts">
import type { DayPlan } from '../../types/trip'

defineProps<{
  activeSection: 'overview' | number
  days: DayPlan[]
}>()

const emit = defineEmits<{
  selectSection: [section: 'overview' | number]
}>()
</script>

<template>
  <aside class="result-sidebar" aria-label="行程导航">
    <button
      class="sidebar-item"
      :class="{ active: activeSection === 'overview' }"
      type="button"
      @click="emit('selectSection', 'overview')"
    >
      <span>Overview</span>
      <strong>行程概览</strong>
    </button>

    <button
      v-for="day in days"
      :key="day.day"
      class="sidebar-item"
      :class="{ active: activeSection === day.day }"
      type="button"
      @click="emit('selectSection', day.day)"
    >
      <span>Day {{ day.day }}</span>
      <strong>第 {{ day.day }} 天</strong>
    </button>
  </aside>
</template>

<style scoped>
.result-sidebar {
  position: sticky;
  top: 24px;
  display: grid;
  gap: 10px;
  align-self: start;
}

.sidebar-item {
  display: grid;
  gap: 4px;
  width: 100%;
  padding: 14px;
  text-align: left;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
}

.sidebar-item span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.sidebar-item strong {
  color: var(--text);
  font-size: 16px;
}

.sidebar-item.active {
  background: var(--primary);
  border-color: var(--primary);
}

.sidebar-item.active span,
.sidebar-item.active strong {
  color: #ffffff;
}

@media (max-width: 860px) {
  .result-sidebar {
    position: static;
    grid-auto-flow: column;
    grid-auto-columns: minmax(140px, 1fr);
    overflow-x: auto;
    padding-bottom: 4px;
  }
}
</style>
