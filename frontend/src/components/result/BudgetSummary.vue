<script setup lang="ts">
import { computed } from 'vue'
import type { Budget } from '../../types/trip'

const props = defineProps<{
  budget: Budget
}>()

const budgetItems = computed(() => {
  const total = props.budget.total || 1

  return [
    {
      label: '酒店住宿',
      value: props.budget.total_hotels,
      color: '#176b5d',
    },
    {
      label: '景点门票',
      value: props.budget.total_attractions,
      color: '#d88b2d',
    },
    {
      label: '餐饮费用',
      value: props.budget.total_meals,
      color: '#2563eb',
    },
    {
      label: '交通费用',
      value: props.budget.total_transportation,
      color: '#7c3aed',
    },
  ].map((item) => ({
    ...item,
    percent: Math.round((item.value / total) * 100),
  }))
})
</script>

<template>
  <section class="budget-panel" aria-label="预算概览">
    <div class="budget-total">
      <span>预算合计</span>
      <strong>¥{{ budget.total }}</strong>
    </div>

    <div class="budget-bars">
      <article v-for="item in budgetItems" :key="item.label" class="budget-row">
        <div class="budget-row-header">
          <span>{{ item.label }}</span>
          <strong>¥{{ item.value }}</strong>
        </div>
        <div class="budget-track" :aria-label="`${item.label} 占比 ${item.percent}%`">
          <i :style="{ width: `${item.percent}%`, backgroundColor: item.color }"></i>
        </div>
        <em>{{ item.percent }}%</em>
      </article>
    </div>
  </section>
</template>

<style scoped>
.budget-panel {
  display: grid;
  gap: 16px;
  height: 100%;
  padding: 22px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.budget-total {
  display: grid;
  gap: 8px;
  padding: 18px;
  color: #ffffff;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  border-radius: 8px;
}

.budget-total span {
  color: rgba(255, 255, 255, 0.78);
  font-size: 13px;
  font-weight: 800;
}

.budget-total strong {
  margin: 0;
  color: #ffffff;
  font-size: 34px;
  line-height: 1;
  font-weight: 900;
}

.budget-bars {
  display: grid;
  gap: 13px;
}

.budget-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 42px;
  gap: 7px 10px;
  align-items: center;
}

.budget-row-header {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  grid-column: 1 / -1;
}

.budget-row-header span {
  color: var(--text);
  font-size: 13px;
  font-weight: 800;
}

.budget-row-header strong {
  color: var(--primary-dark);
  font-size: 14px;
  font-weight: 900;
}

.budget-track {
  height: 9px;
  overflow: hidden;
  background: #edf2ed;
  border-radius: 999px;
}

.budget-track i {
  display: block;
  height: 100%;
  min-width: 4px;
  border-radius: inherit;
}

.budget-row em {
  color: var(--muted);
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
  text-align: right;
}
</style>
