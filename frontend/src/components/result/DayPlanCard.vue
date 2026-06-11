<script setup lang="ts">
import type { DayPlan } from '../../types/trip'
import AttractionCard from './AttractionCard.vue'

const props = defineProps<{
  day: DayPlan
}>()

const getWeatherIcon = (weatherText: string) => {
  const text = weatherText.trim()

  if (text.includes('雷')) return '⛈️'
  if (text.includes('雪')) return '❄️'
  if (text.includes('雨')) return '🌧️'
  if (text.includes('阴')) return '☁️'
  if (text.includes('云')) return '⛅'
  if (text.includes('晴')) return '☀️'
  if (text.includes('风')) return '💨'

  return '🌤️'
}
</script>

<template>
  <article class="day-card">
    <div class="day-index">
      <span>Day</span>
      <strong>{{ props.day.day }}</strong>
    </div>

    <div class="day-content">
      <header class="day-header">
        <div>
          <h2>{{ props.day.title }}</h2>
        </div>
        <div class="weather-pill">
          <span class="weather-icon" aria-hidden="true">
            {{ getWeatherIcon(props.day.weather.weather) }}
          </span>
          <span>{{ props.day.weather.weather }} / {{ props.day.weather.temperature }}</span>
        </div>
      </header>

      <p class="weather-note">{{ props.day.weather.suggestion }}</p>

      <div class="section-block">
        <h3>景点安排</h3>
        <div class="attraction-timeline">
          <div
            v-for="(attraction, index) in props.day.attractions"
            :key="attraction.name"
            class="timeline-stop"
          >
            <div class="timeline-marker">
              <span>{{ index + 1 }}</span>
            </div>
            <AttractionCard :attraction="attraction" />
          </div>
        </div>
      </div>

      <div class="day-side-grid">
        <div class="section-block">
          <h3>🏨 酒店推荐</h3>
          <div class="info-card info-card--hotel">
            <div class="info-card-header info-card-header--hotel">
              <p class="info-title">{{ props.day.hotel.name }}</p>
              <span class="info-price-tag">¥{{ props.day.hotel.price }} / 晚</span>
            </div>
            <p class="info-subtext">{{ props.day.hotel.address }}</p>
            <p>{{ props.day.hotel.description }}</p>
          </div>
        </div>

        <div class="section-block">
          <h3>🍜 餐饮建议</h3>
          <div class="info-card info-card--meals">
            <div class="meal-tags">
              <span v-for="meal in props.day.meals" :key="meal" class="meal-tag">
                {{ meal }}
              </span>
            </div>
            <p>优先安排本地特色餐饮，并兼顾景点周边步行可达的用餐选择。</p>
          </div>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
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
  margin: 0;
  color: var(--text);
  font-size: 24px;
}

.weather-pill {
  flex: 0 0 auto;
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 8px 12px;
  color: var(--primary-dark);
  background: var(--soft);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 800;
}

.weather-icon {
  font-size: 16px;
  line-height: 1;
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

.attraction-timeline {
  position: relative;
  display: grid;
  gap: 14px;
}

.attraction-timeline::before {
  position: absolute;
  top: 20px;
  bottom: 20px;
  left: 19px;
  width: 2px;
  content: "";
  background: linear-gradient(180deg, rgba(23, 107, 93, 0.26), rgba(216, 139, 45, 0.2));
}

.timeline-stop {
  position: relative;
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.timeline-marker {
  position: relative;
  z-index: 1;
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  background: #ffffff;
  border-radius: 999px;
}

.timeline-marker span {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  color: #ffffff;
  background: var(--primary);
  border-radius: inherit;
  font-size: 13px;
  font-weight: 900;
}

.day-side-grid {
  display: grid;
  gap: 18px;
  padding-top: 4px;
}

.info-card {
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.info-card--hotel {
  background: linear-gradient(180deg, #fffaf1, #ffffff);
}

.info-card--meals {
  background: linear-gradient(180deg, #f7fbf8, #ffffff);
}

.info-card--meals p {
  font-size: 15px;
}

.info-card-header {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.info-card-header--hotel {
  justify-content: space-between;
}

.info-title {
  color: var(--text) !important;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.5;
  margin: 0;
}

.info-subtext {
  color: var(--primary-dark) !important;
  font-size: 13px;
}

.info-price-tag {
  flex: 0 0 auto;
  padding: 6px 10px;
  color: var(--primary-dark);
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(23, 107, 93, 0.12);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.meal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meal-tag {
  display: inline-flex;
  align-items: center;
  padding: 7px 11px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid rgba(23, 107, 93, 0.12);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 800;
}

@media (max-width: 860px) {
  .day-card {
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

  .timeline-stop {
    grid-template-columns: 1fr;
  }

  .attraction-timeline::before,
  .timeline-marker {
    display: none;
  }
}
</style>
