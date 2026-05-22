<script setup lang="ts">
import { computed } from 'vue'
import TripResult from '../components/TripResult.vue'
import type { TripPlan } from '../types/trip'

const tripPlan = computed<TripPlan | null>(() => {
  const data = sessionStorage.getItem('tripPlan')
  return data ? JSON.parse(data) : null
})
</script>

<template>
  <TripResult v-if="tripPlan" :trip-plan="tripPlan" />

  <main v-else class="empty-result">
    <p>还没有生成旅行计划，请先返回首页填写信息。</p>
  </main>
</template>

<style scoped>
.empty-result {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg);
  color: var(--text);
}
</style>
