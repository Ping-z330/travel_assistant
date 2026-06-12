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
    <section class="hero-panel" aria-label="智能旅游助手介绍">
      <a class="brand-logo" href="/" aria-label="智能旅游助手首页">
        <span class="brand-mark">旅</span>
        <span class="brand-name">AI Travel Assistant</span>
      </a>
      <RouterLink class="history-link" to="/my-trips">我的行程</RouterLink>

      <div class="hero-copy">
        <p class="brand-en">Plan with real context</p>
        <h1>让每一段旅程，都有清晰的去处。</h1>
        <p class="hero-description">
          输入目的地、日期与偏好，系统会结合景点、天气、住宿与预算，为你整理一份可查看路线、可导出的旅行计划。
        </p>
      </div>

      <div class="feature-strip" aria-label="能力亮点">
        <span>真实 POI</span>
        <span>天气建议</span>
        <span>路线地图</span>
        <span>PDF 导出</span>
      </div>

      <div class="hero-card" aria-hidden="true">
        <div class="route-card">
          <span class="route-kicker">Today Route</span>
          <strong>城市漫游计划</strong>
          <div class="route-line">
            <i></i>
            <i></i>
            <i></i>
          </div>
          <span class="route-note">景点、住宿与预算同步生成</span>
        </div>
      </div>
    </section>

    <section class="form-panel" aria-labelledby="trip-form-title">
      <div class="form-heading">
        <p class="eyebrow">Step 1 · 旅行信息</p>
        <h2 id="trip-form-title">先说说你的出发计划</h2>
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
  grid-template-columns: minmax(360px, 0.86fr) minmax(620px, 680px);
  gap: clamp(28px, 4vw, 62px);
  align-items: center;
  min-height: 100vh;
  padding: 38px clamp(20px, 4vw, 64px) 44px;
  overflow: hidden;
  background:
    linear-gradient(
      115deg,
      rgba(15, 49, 42, 0.9) 0%,
      rgba(15, 49, 42, 0.72) 48%,
      rgba(246, 242, 230, 0.9) 48.2%,
      rgba(247, 248, 242, 0.96) 100%
    ),
    url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1800&q=86");
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.trip-page::before {
  position: absolute;
  inset: 0;
  content: "";
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: linear-gradient(90deg, #000 0%, transparent 72%);
}

.hero-panel,
.form-panel,
.site-footer {
  position: relative;
  z-index: 1;
}

.hero-panel {
  display: grid;
  gap: 34px;
  max-width: 720px;
  color: #ffffff;
}

.brand-logo {
  display: inline-flex;
  width: fit-content;
  gap: 12px;
  align-items: center;
  color: #ffffff;
  text-decoration: none;
}

.history-link {
  position: absolute;
  top: 0;
  right: 0;
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  padding: 0 14px;
  color: #ffffff;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  backdrop-filter: blur(10px);
  font-size: 13px;
  font-weight: 900;
}

.brand-mark {
  display: inline-grid;
  width: 48px;
  height: 48px;
  place-items: center;
  color: #17372f;
  font-size: 24px;
  font-weight: 900;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  background: #f2ca76;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.brand-name {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0;
}

.hero-copy {
  display: grid;
  gap: 18px;
}

.brand-en {
  margin: 0;
  color: #f2ca76;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.hero-copy h1 {
  max-width: 700px;
  margin: 0;
  font-size: clamp(44px, 6vw, 78px);
  line-height: 0.98;
  font-weight: 900;
  letter-spacing: 0;
}

.hero-description {
  max-width: 620px;
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: 17px;
  line-height: 1.85;
}

.feature-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.feature-strip span {
  display: inline-flex;
  min-height: 34px;
  align-items: center;
  padding: 0 12px;
  color: rgba(255, 255, 255, 0.86);
  background: rgba(255, 255, 255, 0.11);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  backdrop-filter: blur(12px);
  font-size: 13px;
  font-weight: 800;
}

.hero-card {
  width: min(100%, 420px);
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(14px);
}

.route-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  color: #17372f;
  background: rgba(255, 251, 238, 0.94);
  border-radius: 6px;
  box-shadow: 0 24px 60px rgba(4, 21, 18, 0.2);
}

.route-kicker,
.route-note {
  color: #6c7368;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.route-card strong {
  font-size: 22px;
}

.route-line {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: center;
  padding: 8px 0;
}

.route-line::before {
  position: absolute;
  right: 16px;
  left: 16px;
  height: 2px;
  content: "";
  background: linear-gradient(90deg, #176b5d, #d88b2d);
}

.route-line i {
  z-index: 1;
  width: 16px;
  height: 16px;
  background: #176b5d;
  border: 3px solid #fffbee;
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(23, 107, 93, 0.18);
}

.route-line i:nth-child(2) {
  justify-self: center;
  background: #d88b2d;
}

.route-line i:nth-child(3) {
  justify-self: end;
  background: #176b5d;
}

.form-panel {
  width: min(100%, 680px);
  justify-self: end;
  padding: 26px;
  transform: translateX(150px);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(23, 107, 93, 0.12);
  border-radius: 8px;
  box-shadow: 0 32px 80px rgba(8, 29, 26, 0.2);
  backdrop-filter: blur(18px);
}

.form-heading {
  display: grid;
  gap: 10px;
  margin-bottom: 18px;
}

.eyebrow {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  margin: 0;
  padding: 0 12px;
  color: var(--primary-dark);
  background: #edf4ef;
  border: 1px solid #d6e4d9;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

h2,
p {
  margin-top: 0;
}

h2 {
  margin-bottom: 0;
  color: #17241d;
  font-size: 24px;
  line-height: 1.18;
}

.trip-form {
  display: grid;
  gap: 14px;
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
  gap: 12px;
  min-width: 0;
  margin: 0;
  padding: 12px;
  background: rgba(248, 250, 246, 0.7);
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
  background: #f8faf6;
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
  background: #f8faf6;
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
  background: #f8faf6;
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
  min-height: 52px;
  margin-top: 4px;
  color: #ffffff;
  background: linear-gradient(135deg, #176b5d, #0f4b42);
  border: 0;
  border-radius: 6px;
  box-shadow: 0 16px 32px rgba(23, 107, 93, 0.22);
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
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #e3e9e1;
}

.form-footnote span {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  gap: 8px;
  padding: 0 11px;
  color: var(--primary-dark);
  background: #f8faf6;
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
  right: clamp(20px, 5vw, 84px);
  bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  align-items: center;
  justify-content: flex-end;
  color: rgba(23, 55, 47, 0.58);
  font-size: 13px;
  letter-spacing: 0.04em;
  text-align: center;
}

@media (max-width: 1120px) {
  .trip-page {
    grid-template-columns: 1fr;
    gap: 28px;
    padding: 36px 18px 72px;
    background:
      linear-gradient(rgba(15, 49, 42, 0.78), rgba(15, 49, 42, 0.72)),
      url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=82");
    background-position: center;
    background-size: cover;
  }

  .trip-page::before {
    opacity: 0.5;
    mask-image: none;
  }

  .hero-panel {
    max-width: 760px;
  }

  .hero-card {
    display: none;
  }

  .form-panel {
    width: min(100%, 640px);
    justify-self: stretch;
    transform: none;
  }

  .param-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .site-footer {
    right: 18px;
    left: 18px;
    justify-content: center;
    color: rgba(255, 255, 255, 0.72);
  }
}

@media (max-width: 560px) {
  .trip-page {
    padding: 24px 14px 68px;
  }

  .hero-panel {
    gap: 22px;
  }

  .brand-mark {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    font-size: 22px;
  }

  .brand-name {
    font-size: 16px;
  }

  .brand-en {
    font-size: 11px;
    letter-spacing: 0.14em;
  }

  .hero-copy h1 {
    font-size: 38px;
    line-height: 1.04;
  }

  .hero-description {
    font-size: 15px;
    line-height: 1.72;
  }

  .feature-strip span {
    min-height: 32px;
    font-size: 12px;
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
