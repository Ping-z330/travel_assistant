<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  deleteSavedTripPlan,
  listSavedTripPlans,
} from '../services/tripHistory'
import type { SavedTripPlan } from '../types/trip'

const router = useRouter()
const savedTrips = ref<SavedTripPlan[]>(listSavedTripPlans())

const hasTrips = computed(() => savedTrips.value.length > 0)

const formatSavedTime = (value: string) =>
  new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))

const openTrip = (trip: SavedTripPlan) => {
  sessionStorage.setItem('tripPlan', JSON.stringify(trip.trip_plan))
  sessionStorage.setItem('savedTripId', trip.id)
  router.push('/result')
}

const removeTrip = (id: string) => {
  savedTrips.value = deleteSavedTripPlan(id)
}

const backHome = () => {
  router.push('/')
}
</script>

<template>
  <main class="my-trips-page">
    <header class="my-trips-header">
      <div>
        <p class="eyebrow">My Trips</p>
        <h1>我的行程</h1>
        <span>只保存你手动确认过的旅行计划。</span>
      </div>

      <button class="primary-action" type="button" @click="backHome">生成新行程</button>
    </header>

    <section v-if="hasTrips" class="trip-list" aria-label="已保存行程">
      <article v-for="trip in savedTrips" :key="trip.id" class="trip-card">
        <div class="trip-card-main">
          <p class="trip-kicker">{{ trip.city }}</p>
          <h2>{{ trip.title }}</h2>
          <div class="trip-meta">
            <span>{{ trip.start_date }} 出发</span>
            <span>{{ trip.days_count }} 天</span>
            <span>¥{{ trip.budget_total }}</span>
            <span>{{ formatSavedTime(trip.updated_at ?? trip.saved_at) }} 更新</span>
          </div>
        </div>

        <div class="trip-card-actions">
          <button class="open-action" type="button" @click="openTrip(trip)">查看</button>
          <button class="delete-action" type="button" @click="removeTrip(trip.id)">删除</button>
        </div>
      </article>
    </section>

    <section v-else class="empty-state">
      <p class="eyebrow">No Saved Trips</p>
      <h2>还没有保存的行程</h2>
      <p>生成旅行计划后，在结果页点击“保存到我的行程”，这里就会出现记录。</p>
      <button class="primary-action" type="button" @click="backHome">去生成行程</button>
    </section>
  </main>
</template>

<style scoped>
.my-trips-page {
  min-height: 100vh;
  padding: 34px 20px 56px;
  background:
    linear-gradient(180deg, rgba(23, 107, 93, 0.14), transparent 320px),
    var(--bg);
}

.my-trips-header,
.trip-list,
.empty-state {
  width: min(1040px, 100%);
  margin: 0 auto;
}

.my-trips-header {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0;
  color: var(--accent);
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.my-trips-header h1,
.empty-state h2 {
  margin: 4px 0 8px;
  color: var(--text);
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.1;
}

.my-trips-header span,
.empty-state p {
  color: var(--muted);
  line-height: 1.7;
}

.trip-list {
  display: grid;
  gap: 14px;
}

.trip-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 20px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 18px 42px rgba(31, 48, 39, 0.08);
}

.trip-card-main {
  min-width: 0;
}

.trip-kicker {
  margin: 0 0 6px;
  color: var(--primary-dark);
  font-size: 13px;
  font-weight: 900;
}

.trip-card h2 {
  margin: 0;
  color: var(--text);
  font-size: 22px;
  line-height: 1.35;
}

.trip-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.trip-meta span {
  display: inline-flex;
  min-height: 30px;
  align-items: center;
  padding: 0 10px;
  color: var(--primary-dark);
  background: var(--soft);
  border: 1px solid rgba(23, 107, 93, 0.1);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
}

.trip-card-actions {
  display: flex;
  gap: 9px;
}

.primary-action,
.open-action,
.delete-action {
  min-height: 40px;
  padding: 0 16px;
  border-radius: 6px;
  font-weight: 900;
}

.primary-action,
.open-action {
  color: #ffffff;
  background: var(--primary);
  border: 1px solid var(--primary);
}

.delete-action {
  color: #9f2f21;
  background: #fff8f5;
  border: 1px solid rgba(159, 47, 33, 0.22);
}

.empty-state {
  display: grid;
  justify-items: start;
  gap: 12px;
  padding: 34px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.empty-state p {
  max-width: 560px;
  margin: 0;
}

@media (max-width: 720px) {
  .my-trips-header,
  .trip-card {
    grid-template-columns: 1fr;
    display: grid;
  }

  .trip-card-actions {
    justify-content: flex-start;
  }
}
</style>
