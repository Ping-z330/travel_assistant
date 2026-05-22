<script setup lang="ts">
import type { DayPlan } from '../../types/trip'
import AttractionCard from './AttractionCard.vue'

defineProps<{
  day: DayPlan
}>()
</script>

<template>
  <article class="day-card">
    <div class="day-index">
      <span>Day</span>
      <strong>{{ day.day }}</strong>
    </div>

    <div class="day-content">
      <header class="day-header">
        <div>
          <p class="day-label">第 {{ day.day }} 天</p>
          <h2>{{ day.title }}</h2>
        </div>
        <div class="weather-pill">
          {{ day.weather.weather }} / {{ day.weather.temperature }}
        </div>
      </header>

      <p class="weather-note">{{ day.weather.suggestion }}</p>

      <div class="section-block">
        <h3>景点安排</h3>
        <div class="attraction-list">
          <AttractionCard
            v-for="attraction in day.attractions"
            :key="attraction.name"
            :attraction="attraction"
          />
        </div>
      </div>

      <div class="day-side-grid">
        <div class="section-block">
          <h3>酒店推荐</h3>
          <p>
            <strong>{{ day.hotel.name }}</strong>
            <span>{{ day.hotel.price }} 元</span>
          </p>
          <p>{{ day.hotel.description }}</p>
        </div>

        <div class="section-block">
          <h3>餐饮建议</h3>
          <p>{{ day.meals.join(' / ') }}</p>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.day-label {
  margin: 0;
  color: var(--accent);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.day-card {
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr);
  gap: 20px;
  padding: 22px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.day-index {
  display: grid;
  width: 62px;
  height: 78px;
  place-items: center;
  align-content: center;
  color: #ffffff;
  background: var(--primary);
  border-radius: 8px;
}

.day-index span {
  font-size: 12px;
  font-weight: 800;
  opacity: 0.78;
}

.day-index strong {
  font-size: 30px;
  line-height: 1;
}

.day-content {
  display: grid;
  gap: 18px;
}

.day-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
}

.day-header h2 {
  margin: 4px 0 0;
  color: var(--text);
  font-size: 24px;
}

.weather-pill {
  flex: 0 0 auto;
  padding: 8px 12px;
  color: var(--primary-dark);
  background: var(--soft);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 800;
}

.weather-note {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.section-block {
  display: grid;
  gap: 10px;
}

.section-block h3 {
  margin: 0;
  color: var(--primary-dark);
  font-size: 16px;
}

.section-block p {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.section-block strong {
  color: var(--text);
}

.section-block span {
  color: var(--muted);
}

.attraction-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.day-side-grid {
  padding-top: 4px;
}

@media (max-width: 860px) {
  .day-card,
  .day-side-grid {
    grid-template-columns: 1fr;
  }

  .day-index {
    width: 100%;
    height: auto;
    min-height: 54px;
    grid-auto-flow: column;
    justify-content: center;
    gap: 8px;
  }

  .day-header {
    display: grid;
  }
}

@media (max-width: 560px) {
  .day-card {
    padding: 20px;
  }

  .attraction-list {
    grid-template-columns: 1fr;
  }
}
</style>
