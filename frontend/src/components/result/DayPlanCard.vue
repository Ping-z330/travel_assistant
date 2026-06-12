<script setup lang="ts">
import type { Attraction, DayPlan, Location } from '../../types/trip'
import AttractionCard from './AttractionCard.vue'

const props = defineProps<{
  day: DayPlan
  editing?: boolean
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

const getDefaultLocation = (): Location => {
  return (
    props.day.attractions[props.day.attractions.length - 1]?.location ??
    props.day.hotel.location ?? {
      longitude: 116.397128,
      latitude: 39.916527,
    }
  )
}

const addAttraction = () => {
  props.day.attractions.push({
    name: '自定义景点',
    address: `${props.day.title}附近`,
    location: { ...getDefaultLocation() },
    visit_duration: 90,
    ticket_price: 0,
    description: '根据实际兴趣补充的自定义景点。',
    image_url: '',
    category: '自定义',
  })
}

const removeAttraction = (index: number) => {
  props.day.attractions.splice(index, 1)
}

const moveAttraction = (index: number, direction: -1 | 1) => {
  const nextIndex = index + direction
  if (nextIndex < 0 || nextIndex >= props.day.attractions.length) {
    return
  }

  const [item] = props.day.attractions.splice(index, 1)
  props.day.attractions.splice(nextIndex, 0, item)
}

const addMeal = () => {
  props.day.meals.push('加餐：补充用餐建议')
}

const removeMeal = (index: number) => {
  props.day.meals.splice(index, 1)
}

const ensureNumber = (value: number | string) => Number(value || 0)

const updateAttractionName = (attraction: Attraction, value: string) => {
  if (attraction.name !== value) {
    attraction.image_url = ''
  }

  attraction.name = value
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
          <label v-if="props.editing" class="edit-field edit-field--title">
            <span>当天标题</span>
            <input v-model="props.day.title" type="text" />
          </label>
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
        <div class="section-heading">
          <h3>景点安排</h3>
          <button v-if="props.editing" class="mini-action" type="button" @click="addAttraction">
            新增景点
          </button>
        </div>
        <div class="attraction-timeline">
          <div
            v-for="(attraction, index) in props.day.attractions"
            :key="`${props.day.day}-${index}`"
            class="timeline-stop"
          >
            <div class="timeline-marker">
              <span>{{ index + 1 }}</span>
            </div>
            <div v-if="props.editing" class="edit-attraction-card">
              <div class="edit-card-toolbar">
                <strong>景点 {{ index + 1 }}</strong>
                <div class="edit-toolbar-actions">
                  <button type="button" :disabled="index === 0" @click="moveAttraction(index, -1)">
                    上移
                  </button>
                  <button
                    type="button"
                    :disabled="index === props.day.attractions.length - 1"
                    @click="moveAttraction(index, 1)"
                  >
                    下移
                  </button>
                  <button class="danger-action" type="button" @click="removeAttraction(index)">
                    删除
                  </button>
                </div>
              </div>

              <div class="edit-grid">
                <label class="edit-field">
                  <span>景点名称</span>
                  <input
                    :value="attraction.name"
                    type="text"
                    @input="updateAttractionName(attraction, ($event.target as HTMLInputElement).value)"
                  />
                </label>
                <label class="edit-field">
                  <span>分类</span>
                  <input v-model="attraction.category" type="text" />
                </label>
                <label class="edit-field edit-field--wide">
                  <span>地址</span>
                  <input v-model="attraction.address" type="text" />
                </label>
                <label class="edit-field">
                  <span>游玩时长（分钟）</span>
                  <input
                    :value="attraction.visit_duration"
                    min="0"
                    type="number"
                    @input="attraction.visit_duration = ensureNumber(($event.target as HTMLInputElement).value)"
                  />
                </label>
                <label class="edit-field">
                  <span>门票（元）</span>
                  <input
                    :value="attraction.ticket_price"
                    min="0"
                    type="number"
                    @input="attraction.ticket_price = ensureNumber(($event.target as HTMLInputElement).value)"
                  />
                </label>
                <label class="edit-field edit-field--wide">
                  <span>推荐理由</span>
                  <textarea v-model="attraction.description" rows="3"></textarea>
                </label>
              </div>
            </div>
            <AttractionCard v-else :attraction="attraction" />
          </div>
        </div>
      </div>

      <div class="day-side-grid">
        <div class="section-block">
          <h3>🏨 酒店推荐</h3>
          <div v-if="props.editing" class="info-card info-card--hotel edit-panel">
            <div class="edit-grid">
              <label class="edit-field">
                <span>酒店名称</span>
                <input v-model="props.day.hotel.name" type="text" />
              </label>
              <label class="edit-field">
                <span>价格（元/晚）</span>
                <input
                  :value="props.day.hotel.price"
                  min="0"
                  type="number"
                  @input="props.day.hotel.price = ensureNumber(($event.target as HTMLInputElement).value)"
                />
              </label>
              <label class="edit-field edit-field--wide">
                <span>酒店地址</span>
                <input v-model="props.day.hotel.address" type="text" />
              </label>
              <label class="edit-field edit-field--wide">
                <span>推荐理由</span>
                <textarea v-model="props.day.hotel.description" rows="3"></textarea>
              </label>
            </div>
          </div>
          <div v-else class="info-card info-card--hotel">
            <div class="info-card-header info-card-header--hotel">
              <p class="info-title">{{ props.day.hotel.name }}</p>
              <span class="info-price-tag">¥{{ props.day.hotel.price }} / 晚</span>
            </div>
            <p class="info-subtext">{{ props.day.hotel.address }}</p>
            <p>{{ props.day.hotel.description }}</p>
          </div>
        </div>

        <div class="section-block">
          <div class="section-heading">
            <h3>🍜 餐饮建议</h3>
            <button v-if="props.editing" class="mini-action" type="button" @click="addMeal">
              新增餐饮
            </button>
          </div>
          <div v-if="props.editing" class="info-card info-card--meals edit-panel">
            <div class="meal-edit-list">
              <label v-for="(_, index) in props.day.meals" :key="index" class="edit-field meal-edit-row">
                <span>餐饮 {{ index + 1 }}</span>
                <input v-model="props.day.meals[index]" type="text" />
                <button class="danger-action" type="button" @click="removeMeal(index)">
                  删除
                </button>
              </label>
            </div>
          </div>
          <div v-else class="info-card info-card--meals">
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

.section-heading {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
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

.edit-field {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.edit-field span {
  color: var(--primary-dark);
  font-size: 12px;
  font-weight: 900;
}

.edit-field input,
.edit-field textarea {
  width: 100%;
  min-width: 0;
  color: var(--text);
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(23, 107, 93, 0.18);
  border-radius: 8px;
  font: inherit;
  font-size: 14px;
  outline: none;
}

.edit-field input {
  min-height: 40px;
  padding: 0 11px;
}

.edit-field textarea {
  resize: vertical;
  padding: 10px 11px;
  line-height: 1.6;
}

.edit-field input:focus,
.edit-field textarea:focus {
  border-color: rgba(23, 107, 93, 0.52);
  box-shadow: 0 0 0 3px rgba(23, 107, 93, 0.1);
}

.edit-field--title {
  margin-top: 12px;
  width: min(520px, 100%);
}

.edit-field--wide {
  grid-column: 1 / -1;
}

.edit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.edit-attraction-card {
  display: grid;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(180deg, #f8fbf8, #ffffff);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.edit-card-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
}

.edit-card-toolbar strong {
  color: var(--primary-dark);
  font-size: 14px;
}

.edit-toolbar-actions {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.mini-action,
.edit-toolbar-actions button,
.danger-action {
  min-height: 32px;
  padding: 0 10px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid rgba(23, 107, 93, 0.18);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}

.mini-action {
  background: #fff8ec;
  border-color: rgba(216, 139, 45, 0.34);
}

.edit-toolbar-actions button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.danger-action {
  color: #9f2f21;
  border-color: rgba(159, 47, 33, 0.22);
}

.edit-panel {
  background: linear-gradient(180deg, #fbf8ef, #ffffff);
}

.meal-edit-list {
  display: grid;
  gap: 10px;
}

.meal-edit-row {
  grid-template-columns: 72px minmax(0, 1fr) auto;
  align-items: end;
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

  .edit-grid {
    grid-template-columns: 1fr;
  }

  .meal-edit-row {
    grid-template-columns: 1fr;
  }

  .edit-card-toolbar {
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
