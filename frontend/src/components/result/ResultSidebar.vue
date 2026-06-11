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
    <p class="sidebar-title">行程目录</p>

    <button
      class="sidebar-item sidebar-item--overview"
      :class="{ active: activeSection === 'overview' }"
      type="button"
      @click="emit('selectSection', 'overview')"
    >
      <span class="sidebar-kicker">Overview</span>
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
      <strong>第 {{ day.day }} 天 · {{ day.title }}</strong>
    </button>
  </aside>
</template>

<style scoped>
.result-sidebar {
  position: sticky;
  top: 24px;
  display: grid;
  gap: 9px;
  align-self: start;
}

.sidebar-title {
  margin: 0 0 4px;
  color: var(--primary-dark);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.sidebar-item {
  display: grid;
  gap: 6px;
  width: 100%;
  padding: 13px;
  text-align: left;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.sidebar-item:hover {
  border-color: rgba(23, 107, 93, 0.28);
  box-shadow: 0 12px 28px rgba(31, 48, 39, 0.08);
  transform: translateY(-1px);
}

.sidebar-kicker {
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.sidebar-item strong {
  display: -webkit-box;
  overflow: hidden;
  color: var(--text);
  font-size: 15px;
  line-height: 1.4;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.sidebar-item.active {
  background: var(--primary);
  border-color: var(--primary);
  box-shadow: 0 14px 32px rgba(23, 107, 93, 0.18);
}

.sidebar-item.active .sidebar-kicker,
.sidebar-item.active strong {
  color: #ffffff;
}

@media (max-width: 860px) {
  .result-sidebar {
    position: static;
    grid-auto-flow: column;
    grid-auto-columns: minmax(190px, 1fr);
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .sidebar-title {
    display: none;
  }
}
</style>
