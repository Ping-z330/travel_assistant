<script setup lang="ts">
import { ref } from 'vue'
import TripResult from '../components/TripResult.vue'
import type { TripPlan } from '../types/trip'

const loadTripPlan = (): TripPlan | null => {
  const data = sessionStorage.getItem('tripPlan')
  if (!data) {
    return null
  }

  try {
    return JSON.parse(data) as TripPlan
  } catch {
    sessionStorage.removeItem('tripPlan')
    return null
  }
}

const tripPlan = ref<TripPlan | null>(loadTripPlan())
const savedTripId = ref(sessionStorage.getItem('savedTripId'))

const updateTripPlan = (nextTripPlan: TripPlan) => {
  tripPlan.value = nextTripPlan
  sessionStorage.setItem('tripPlan', JSON.stringify(nextTripPlan))
}

const updateSavedTripId = (id: string) => {
  savedTripId.value = id
  sessionStorage.setItem('savedTripId', id)
}
</script>

<template>
  <TripResult
    v-if="tripPlan"
    :trip-plan="tripPlan"
    :saved-trip-id="savedTripId"
    @update-trip-plan="updateTripPlan"
    @update-saved-trip-id="updateSavedTripId"
  />

  <main v-else class="empty-result">
    <p>还没有生成旅行计划，请先返回首页填写信息。</p>
  </main>
</template>

<style scoped>
.empty-result {
  min-height: calc(100vh - 68px);
  display: grid;
  place-items: center;
  background: var(--bg);
  color: var(--text);
}
</style>
