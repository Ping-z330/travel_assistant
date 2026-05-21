<script setup lang="ts">
import type { Budget } from '../../types/trip'

defineProps<{
  budget: Budget
}>()
</script>

<template>
  <section class="budget-grid" aria-label="预算概览">
    <article class="budget-card budget-card-main">
      <span>预算合计</span>
      <strong>{{ budget.total }} 元</strong>
    </article>
    <article class="budget-card">
      <span>景点门票</span>
      <strong>{{ budget.total_attractions }} 元</strong>
    </article>
    <article class="budget-card">
      <span>酒店住宿</span>
      <strong>{{ budget.total_hotels }} 元</strong>
    </article>
    <article class="budget-card">
      <span>餐饮费用</span>
      <strong>{{ budget.total_meals }} 元</strong>
    </article>
    <article class="budget-card">
      <span>交通费用</span>
      <strong>{{ budget.total_transportation }} 元</strong>
    </article>
  </section>
</template>

<style scoped>
.budget-grid {
  display: grid;
  grid-template-columns: 1.4fr repeat(4, 1fr);
  gap: 14px;
}

.budget-card {
  display: grid;
  gap: 8px;
  min-height: 104px;
  padding: 18px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.budget-card span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.budget-card strong {
  margin: 0;
  color: var(--primary-dark);
  font-size: 22px;
  font-weight: 800;
}

.budget-card-main {
  background: var(--primary);
}

.budget-card-main span,
.budget-card-main strong {
  color: #ffffff;
}

@media (max-width: 860px) {
  .budget-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
