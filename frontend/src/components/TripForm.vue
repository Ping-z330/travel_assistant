<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { generateTripPlan } from '../services/tripApi'
import type { TripPlanRequest } from '../types/trip'

const preferences = ['自然风光', '历史人文', '美食探索', '亲子轻松', '网红打卡']

const form = reactive({
  departureCity: '',
  city: '',
  startDate: '',
  days: 3,
  budget: 3000,
  people: 2,
  preference: '自然风光',
  requirements: '',
})

const loading = ref(false)
const errorMessage = ref('')
const router = useRouter()

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const request: TripPlanRequest = {
      departure_city: form.departureCity.trim() || undefined,
      city: form.city,
      start_date: form.startDate,
      days: form.days,
      budget: form.budget,
      people: form.people,
      preference: form.preference,
      requirements: form.requirements.trim() || undefined,
    }

    const response = await generateTripPlan(request)
    sessionStorage.setItem('tripPlan', JSON.stringify(response))
    sessionStorage.removeItem('savedTripId')
    router.push('/result')
  } catch {
    errorMessage.value = '生成旅行计划时发生错误，请稍后重试。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="trip-page">
    <section class="form-panel" aria-labelledby="trip-form-title">
      <div class="form-heading">
        <p class="eyebrow">Travel Planner</p>
        <h2 id="trip-form-title">规划新行程</h2>
        <span>填写出发地、目的地、日期与偏好，生成完整旅行计划。</span>
      </div>

      <form class="trip-form" @submit.prevent="handleSubmit">
        <div class="city-grid">
          <label class="field">
            <span>出发城市</span>
            <input v-model.trim="form.departureCity" type="text" placeholder="从哪里出发？例如：上海" />
          </label>

          <label class="field">
            <span>目的地城市</span>
            <input v-model.trim="form.city" type="text" placeholder="想去哪里？例如：杭州" required />
          </label>
        </div>

        <fieldset class="field-group">
          <legend>行程参数</legend>
          <div class="param-grid">
            <label class="field">
              <span>出发日期</span>
              <input v-model="form.startDate" type="date" required />
            </label>

            <label class="field">
              <span>游玩天数</span>
              <span class="input-with-unit">
                <input v-model.number="form.days" type="number" min="1" max="15" required />
                <em>天</em>
              </span>
            </label>

            <label class="field">
              <span>总预算</span>
              <span class="input-with-unit input-with-unit--prefix">
                <em>¥</em>
                <input v-model.number="form.budget" type="number" min="0" step="100" required />
              </span>
            </label>

            <label class="field">
              <span>出行人数</span>
              <span class="input-with-unit">
                <input v-model.number="form.people" type="number" min="1" max="20" required />
                <em>人</em>
              </span>
            </label>
          </div>
        </fieldset>

        <div class="field">
          <span>旅行偏好</span>
          <div class="preference-chips" role="radiogroup" aria-label="旅行偏好">
            <button
              v-for="item in preferences"
              :key="item"
              class="preference-chip"
              :class="{ active: form.preference === item }"
              type="button"
              role="radio"
              :aria-checked="form.preference === item"
              @click="form.preference = item"
            >
              {{ item }}
            </button>
          </div>
        </div>

        <label class="field">
          <span>补充需求</span>
          <textarea
            v-model.trim="form.requirements"
            rows="4"
            maxlength="300"
            placeholder="例如：带父母出行，节奏慢一点，想吃本地小吃，尽量避开人多的网红景点。"
          />
        </label>

        <button class="submit-button" type="submit" :disabled="loading">
          <span>{{ loading ? '生成中...' : '生成旅行计划' }}</span>
        </button>

        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>
      </form>

      <div class="form-footnote">
        <span>每日行程</span>
        <span>预算拆分</span>
        <span>地图路线</span>
      </div>
    </section>

    <footer class="site-footer">
      <span>© 2026 AI Travel Assistant. All rights reserved.</span>
    </footer>
  </main>
</template>

<style scoped>
.trip-page {
  position: relative;
  display: grid;
  place-items: center;
  min-height: calc(100vh - 68px);
  padding: 44px clamp(18px, 4vw, 56px) 68px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(23, 107, 93, 0.1), transparent 280px),
    linear-gradient(135deg, rgba(239, 245, 240, 0.98), rgba(249, 250, 246, 0.98));
  background-position: center;
  background-size: auto;
}

.trip-page::before {
  position: absolute;
  inset: 0;
  content: "";
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(23, 107, 93, 0.045) 1px, transparent 1px),
    linear-gradient(rgba(23, 107, 93, 0.045) 1px, transparent 1px);
  background-size: 72px 72px;
  opacity: 0.45;
}

.form-panel,
.site-footer {
  position: relative;
  z-index: 1;
}

.form-panel {
  width: min(100%, 760px);
  justify-self: center;
  padding: 32px;
  transform: none;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(23, 107, 93, 0.14);
  border-radius: 8px;
  box-shadow: 0 22px 58px rgba(31, 48, 39, 0.12);
  backdrop-filter: blur(12px);
}

.form-heading {
  display: grid;
  gap: 8px;
  margin-bottom: 26px;
}

.eyebrow {
  display: inline-flex;
  min-height: 28px;
  align-items: center;
  margin: 0;
  padding: 0;
  color: var(--accent);
  background: transparent;
  border: 0;
  border-radius: 0;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

h2,
p {
  margin-top: 0;
}

h2 {
  margin-bottom: 0;
  color: #17241d;
  font-size: 30px;
  line-height: 1.18;
}

.form-heading span {
  color: var(--muted);
  font-size: 14px;
  line-height: 1.7;
}

.trip-form {
  display: grid;
  gap: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.city-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr);
  gap: 12px;
  align-items: stretch;
}

.field-group {
  display: grid;
  gap: 14px;
  min-width: 0;
  margin: 0;
  padding: 16px;
  background: rgba(248, 251, 248, 0.86);
  border: 1px solid #e0e8df;
  border-radius: 8px;
}

.param-grid {
  display: grid;
  grid-template-columns: 1.35fr 0.8fr 0.95fr 0.8fr;
  gap: 12px;
}

.field-group legend {
  padding: 0 6px;
  color: var(--primary-dark);
  font-size: 13px;
  font-weight: 800;
}

.field {
  display: grid;
  gap: 8px;
  color: var(--text);
  font-size: 15px;
  font-weight: 700;
}

input,
select,
textarea {
  width: 100%;
  min-height: 50px;
  padding: 0 15px;
  color: var(--text);
  background: #ffffff;
  border: 1px solid #d8e2d8;
  border-radius: 6px;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

input:focus,
select:focus,
textarea:focus {
  background: #ffffff;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(23, 107, 93, 0.12);
}

textarea {
  min-height: 86px;
  padding: 13px 15px;
  resize: vertical;
  line-height: 1.6;
}

.input-with-unit {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  min-height: 50px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #d8e2d8;
  border-radius: 6px;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.input-with-unit:focus-within {
  background: #ffffff;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(23, 107, 93, 0.12);
}

.input-with-unit input {
  min-height: 48px;
  padding-right: 8px;
  background: transparent;
  border: 0;
  border-radius: 0;
}

.input-with-unit input:focus {
  box-shadow: none;
}

.input-with-unit em {
  padding: 0 14px 0 8px;
  color: var(--primary-dark);
  font-size: 13px;
  font-style: normal;
  font-weight: 900;
}

.input-with-unit--prefix {
  grid-template-columns: auto minmax(0, 1fr);
}

.input-with-unit--prefix input {
  padding-left: 4px;
  padding-right: 15px;
}

.input-with-unit--prefix em {
  padding: 0 4px 0 14px;
  color: var(--accent);
}

.preference-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preference-chip {
  min-height: 38px;
  padding: 0 13px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid #d8e2d8;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 800;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    transform 0.2s ease;
}

.preference-chip:hover {
  border-color: rgba(23, 107, 93, 0.4);
  transform: translateY(-1px);
}

.preference-chip.active {
  color: #ffffff;
  background: var(--primary);
  border-color: var(--primary);
}

.submit-button {
  width: 100%;
  min-height: 54px;
  margin-top: 2px;
  color: #ffffff;
  background: linear-gradient(135deg, #176b5d, #0f4b42);
  border: 0;
  border-radius: 6px;
  box-shadow: 0 14px 30px rgba(23, 107, 93, 0.18);
  font-weight: 800;
  transition:
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  box-shadow: 0 20px 40px rgba(23, 107, 93, 0.28);
  transform: translateY(-1px);
}

.submit-button:disabled {
  opacity: 0.72;
  cursor: wait;
}

.error-message {
  margin: 10px 0 0;
  color: #b42318;
  font-size: 14px;
  font-weight: 600;
}

.form-footnote {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #e3e9e1;
}

.form-footnote span {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  gap: 8px;
  padding: 0 11px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid #d8e2d8;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.form-footnote span::before {
  width: 6px;
  height: 6px;
  content: "";
  background: #d88b2d;
  border-radius: 50%;
}

.site-footer {
  position: absolute;
  right: 50%;
  bottom: 24px;
  transform: translateX(50%);
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  align-items: center;
  justify-content: flex-end;
  color: rgba(23, 55, 47, 0.6);
  font-size: 13px;
  letter-spacing: 0.04em;
  text-align: center;
}

@media (max-width: 1120px) {
  .trip-page {
    padding: 36px 18px 72px;
  }

  .trip-page::before {
    opacity: 0.55;
  }

  .form-panel {
    width: min(100%, 760px);
    justify-self: center;
    transform: none;
  }

  .param-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .site-footer {
    right: 50%;
    left: auto;
    justify-content: center;
    color: rgba(23, 55, 47, 0.6);
  }
}

@media (max-width: 560px) {
  .trip-page {
    padding: 24px 14px 68px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .city-grid {
    grid-template-columns: 1fr;
  }

  .param-grid {
    grid-template-columns: 1fr;
  }

  .form-panel {
    padding: 22px;
  }

  h2 {
    font-size: 26px;
  }

  .site-footer {
    bottom: 18px;
    gap: 6px 14px;
    font-size: 12px;
  }
}
</style>
