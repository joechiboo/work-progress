<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1
          @click="resetToDefault"
          class="text-3xl font-bold text-gray-900 cursor-pointer hover:opacity-70 transition-opacity"
          title="點擊重新整理"
        >
          📊 工作進度追蹤系統
        </h1>

        <!-- 分頁切換 -->
        <div class="flex gap-2 mt-4">
          <button
            v-for="tab in TABS"
            :key="tab.id"
            @click="switchTab(tab.id)"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="activeTab === tab.id
              ? 'bg-blue-600 text-white shadow'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- 篩選區（工作紀錄／專案明細共用） -->
      <div v-if="summaryData" v-show="activeTab !== 'benefit'" class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">🔍 篩選設定</h2>
          <button
            @click="resetToDefault"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            🔄 還原
          </button>
        </div>

        <!-- 快速區間 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-3">快速區間</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="r in QUICK_RANGES"
              :key="r.id"
              @click="applyQuickRange(r.id)"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="activeRange === r.id
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            >
              {{ r.label }}
            </button>
            <span v-if="activeRange === 'custom'" class="self-center text-sm text-gray-500 ml-1">
              （自訂區間）
            </span>
          </div>
        </div>

        <!-- 專案類型篩選 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-3">專案類型</label>
          <div class="flex gap-3">
            <button
              @click="showSideProjects = false"
              :class="[
                'flex-1 px-4 py-3 rounded-lg font-medium transition-all',
                !showSideProjects
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              <div class="flex items-center justify-center gap-2">
                <span>💼</span>
                <span>僅工作專案</span>
              </div>
            </button>
            <button
              @click="showSideProjects = true"
              :class="[
                'flex-1 px-4 py-3 rounded-lg font-medium transition-all',
                showSideProjects
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              <div class="flex items-center justify-center gap-2">
                <span>🎨</span>
                <span>包含 Side Projects</span>
              </div>
            </button>
          </div>
        </div>

        <!-- 時間區間篩選 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">時間區間</label>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs text-gray-600 mb-1">開始日期</label>
              <input
                type="date"
                v-model="filterStart"
                @change="activeRange = 'custom'"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-xs text-gray-600 mb-1">結束日期</label>
              <input
                type="date"
                v-model="filterEnd"
                @change="activeRange = 'custom'"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 工作紀錄分頁 -->
      <div v-if="summaryData" v-show="activeTab === 'work'" class="space-y-6">
        <!-- 期間與作者 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-2xl font-bold mb-4">
            📈 您的工作成果（{{ summaryData.author }}）
          </h2>
          <p class="text-gray-600">{{ filterStart }} 至 {{ filterEnd }}</p>
          <p class="text-sm text-gray-500 mt-1">
            共 {{ rangeDays }} 天 ({{ Math.ceil(rangeDays / 7) }} 週)
          </p>
        </div>

        <!-- 統計卡片（附與前一個等長區間的對比） -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">總提交次數</div>
            <div class="text-3xl font-bold text-blue-600">{{ stats.totalCommits }}</div>
            <div class="text-xs mt-2" :class="deltaClass(delta.totalCommits)">
              {{ deltaText(delta.totalCommits) }}
              <span class="text-gray-400 font-normal">vs 前 {{ rangeDays }} 天</span>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">專案數量</div>
            <div class="text-3xl font-bold text-green-600">{{ stats.projectCount }}</div>
            <div class="text-xs mt-2" :class="deltaClass(delta.projectCount)">
              {{ deltaText(delta.projectCount) }}
              <span class="text-gray-400 font-normal">vs 前 {{ rangeDays }} 天</span>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">日均提交</div>
            <div class="text-3xl font-bold text-purple-600">{{ stats.dailyAverage }}</div>
            <div class="text-xs mt-2" :class="deltaClass(delta.dailyAverage)">
              {{ deltaText(delta.dailyAverage) }}
              <span class="text-gray-400 font-normal">vs 前 {{ rangeDays }} 天</span>
            </div>
          </div>
        </div>

        <!-- 提交趨勢 -->
        <TrendChart
          :daily="filteredDaily"
          :range-start="filterStart"
          :range-end="filterEnd"
          :show-side-projects="showSideProjects"
        />

        <!-- 專案排行 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold">🏆 專案排行</h3>
            <button
              @click="switchTab('detail')"
              class="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              看 commit 明細 →
            </button>
          </div>
          <div v-if="!projectRanking.length" class="text-center text-gray-400 py-8">
            這個區間沒有資料
          </div>
          <div v-else class="space-y-2">
            <div v-for="p in projectRanking" :key="p.name" class="flex items-center gap-3">
              <div class="w-56 shrink-0 text-sm text-gray-700 truncate" :title="p.name">{{ p.name }}</div>
              <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                <div
                  class="h-full rounded-full"
                  :style="{
                    width: (p.count / projectRanking[0].count * 100) + '%',
                    backgroundColor: p.type === 'side' ? SIDE_COLOR : WORK_COLOR
                  }"
                ></div>
              </div>
              <div class="w-20 text-right text-sm font-semibold text-gray-700">
                {{ p.count }}
                <span class="text-xs text-gray-400 font-normal">{{ p.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分類統計 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-xl font-bold mb-4">📊 分類統計</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="(count, category) in categoryStats"
              :key="category"
              class="p-4 rounded-lg border-2"
              :class="getCategoryColor(category)"
            >
              <div class="text-sm text-gray-600">{{ category }}</div>
              <div class="text-2xl font-bold">{{ count }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 載入中或無資料 -->
      <div v-else-if="activeTab === 'work'" class="text-center py-12">
        <p class="text-gray-500">載入資料中...</p>
      </div>

      <!-- 專案明細分頁（commit 明細檔按需載入） -->
      <ProjectDetail
        v-if="activeTab === 'detail'"
        :projects="filteredDetailProjects"
        :loading="detailLoading"
        :error="detailError"
      />

      <!-- AI 效益分頁 -->
      <div v-show="activeTab === 'benefit'">
        <AiBenefit :data="benefitData" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import AiBenefit from './components/AiBenefit.vue'
import TrendChart from './components/TrendChart.vue'
import ProjectDetail from './components/ProjectDetail.vue'

const TABS = [
  { id: 'work', label: '📋 工作紀錄' },
  { id: 'detail', label: '📝 專案明細' },
  { id: 'benefit', label: '🚀 AI 效益' }
]

// 專案排行的長條顏色，與 TrendChart 的兩個系列一致
const WORK_COLOR = '#2a78d6'
const SIDE_COLOR = '#eb6834'

const activeTab = ref('work')

// 總覽只讀輕量摘要（~100 KB）；commit 明細（~1.5 MB）切到明細分頁才載入
const summaryData = ref(null)
const detailData = ref(null)
const detailLoading = ref(false)
const detailError = ref('')
const benefitData = ref(null)

const filterStart = ref('')
const filterEnd = ref('')
const showSideProjects = ref(false)

const DEFAULT_RANGE = '30d'
const activeRange = ref(DEFAULT_RANGE)

const QUICK_RANGES = [
  { id: '1d', label: '昨日', days: 1 },
  { id: '7d', label: '近 7 天', days: 7 },
  { id: '30d', label: '近 30 天', days: 30 },
  { id: '90d', label: '近 90 天', days: 90 },
  { id: 'ytd', label: '今年' },
  { id: 'all', label: '全部' }
]

// 資料最後一天（每日排程跑完是昨天），拿它當快速區間的錨點，
// 這樣按「近 7 天」不會含進一段根本還沒收集的空白。
const dataEnd = computed(
  () => summaryData.value?.period?.end || dayjs().subtract(1, 'day').format('YYYY-MM-DD')
)
const dataStart = computed(() => summaryData.value?.period?.start || '2025-05-05')

const applyQuickRange = (id) => {
  activeRange.value = id
  const end = dayjs(dataEnd.value)

  if (id === 'all') {
    filterStart.value = dataStart.value
  } else if (id === 'ytd') {
    filterStart.value = end.startOf('year').format('YYYY-MM-DD')
  } else {
    const days = QUICK_RANGES.find(r => r.id === id).days
    filterStart.value = end.subtract(days - 1, 'day').format('YYYY-MM-DD')
  }
  filterEnd.value = dataEnd.value
}

const loadSummary = async (bust = false) => {
  const q = bust ? `?t=${Date.now()}` : ''
  const response = await fetch(import.meta.env.BASE_URL + 'data/work-log-summary.json' + q)
  summaryData.value = await response.json()
}

const loadBenefit = async () => {
  const response = await fetch(import.meta.env.BASE_URL + `data/ai-benefit-data.json?t=${Date.now()}`)
  benefitData.value = await response.json()
}

// 明細檔只在使用者真的要看 commit 時才下載，而且整個 session 只下載一次
const loadDetail = async () => {
  if (detailData.value || detailLoading.value) return
  detailLoading.value = true
  detailError.value = ''
  try {
    const response = await fetch(import.meta.env.BASE_URL + 'data/work-log-latest.json')
    detailData.value = await response.json()
  } catch (error) {
    console.error('載入明細失敗：', error)
    detailError.value = String(error)
  } finally {
    detailLoading.value = false
  }
}

const switchTab = (id) => {
  activeTab.value = id
  if (id === 'detail') loadDetail()
}

// 載入資料
onMounted(async () => {
  try {
    await loadSummary()
    applyQuickRange(DEFAULT_RANGE)
    await loadBenefit()
  } catch (error) {
    console.error('載入資料失敗：', error)
  }
})

// 還原到預設區間並重新載入數據
const resetToDefault = async () => {
  try {
    await loadSummary(true)
    detailData.value = null
    await loadBenefit()
  } catch (error) {
    console.error('重新載入資料失敗：', error)
  }
  showSideProjects.value = false
  applyQuickRange(DEFAULT_RANGE)
  if (activeTab.value === 'detail') loadDetail()
}

// --- 以下統計全部由 summary 的每日計數算出，不需要 commit 明細 ---

const rangeDays = computed(() => {
  if (!filterStart.value || !filterEnd.value) return 1
  return Math.max(1, dayjs(filterEnd.value).diff(dayjs(filterStart.value), 'day') + 1)
})

const sliceDaily = (start, end) => {
  if (!summaryData.value) return []
  return summaryData.value.daily.filter(d => d.date >= start && d.date <= end)
}

const filteredDaily = computed(() => sliceDaily(filterStart.value, filterEnd.value))

// 往前推一個等長區間，用來算漲跌
const previousDaily = computed(() => {
  if (!filterStart.value) return []
  const prevEnd = dayjs(filterStart.value).subtract(1, 'day')
  const prevStart = prevEnd.subtract(rangeDays.value - 1, 'day')
  return sliceDaily(prevStart.format('YYYY-MM-DD'), prevEnd.format('YYYY-MM-DD'))
})

const projectTypes = computed(() => {
  const map = {}
  for (const p of summaryData.value?.projects || []) map[p.name] = p.type
  return map
})

const summarize = (daily, days) => {
  let totalCommits = 0
  const projects = {}
  for (const d of daily) {
    for (const [name, n] of Object.entries(d.projects)) {
      if (!showSideProjects.value && projectTypes.value[name] === 'side') continue
      projects[name] = (projects[name] || 0) + n
      totalCommits += n
    }
  }
  return {
    totalCommits,
    projectCount: Object.keys(projects).length,
    dailyAverage: (totalCommits / Math.max(1, days)).toFixed(1),
    projects
  }
}

const stats = computed(() => summarize(filteredDaily.value, rangeDays.value))
const prevStats = computed(() => summarize(previousDaily.value, rangeDays.value))

const delta = computed(() => {
  const pct = (cur, prev) => (prev > 0 ? Math.round(((cur - prev) / prev) * 100) : null)
  return {
    totalCommits: pct(stats.value.totalCommits, prevStats.value.totalCommits),
    projectCount: pct(stats.value.projectCount, prevStats.value.projectCount),
    dailyAverage: pct(Number(stats.value.dailyAverage), Number(prevStats.value.dailyAverage))
  }
})

const deltaText = (v) => {
  if (v === null) return '無前期資料'
  if (v > 0) return `▲ ${v}%`
  if (v < 0) return `▼ ${Math.abs(v)}%`
  return '持平'
}

const deltaClass = (v) => {
  if (v === null) return 'text-gray-400'
  if (v > 0) return 'text-green-600 font-semibold'
  if (v < 0) return 'text-red-600 font-semibold'
  return 'text-gray-500'
}

const projectRanking = computed(() => {
  const total = stats.value.totalCommits
  return Object.entries(stats.value.projects)
    .map(([name, count]) => ({
      name,
      count,
      type: projectTypes.value[name] || 'work',
      percentage: total > 0 ? Math.round((count / total) * 100) : 0
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 15)
})

const categoryStats = computed(() => {
  const types = showSideProjects.value ? ['work', 'side'] : ['work']
  const out = {}
  for (const d of filteredDaily.value) {
    for (const t of types) {
      for (const [cat, n] of Object.entries(d.categories[t] || {})) {
        out[cat] = (out[cat] || 0) + n
      }
    }
  }
  return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1]))
})

// 明細分頁：把完整資料依同一組篩選條件裁切
const filteredDetailProjects = computed(() => {
  if (!detailData.value) return []
  return detailData.value.projects
    .filter(p => showSideProjects.value || p.type !== 'side')
    .map(p => {
      const commits = (p.commits || []).filter(
        c => c.date >= filterStart.value && c.date <= filterEnd.value
      )
      return { ...p, commits, totalCommits: commits.length }
    })
    .filter(p => p.totalCommits > 0)
    .sort((a, b) => b.totalCommits - a.totalCommits)
})

// 分類顏色
const getCategoryColor = (category) => {
  const colors = {
    '功能開發': 'border-blue-300 bg-blue-50',
    '錯誤修正': 'border-red-300 bg-red-50',
    '重構': 'border-purple-300 bg-purple-50',
    '效能優化': 'border-green-300 bg-green-50',
    '文檔': 'border-yellow-300 bg-yellow-50',
    '測試': 'border-pink-300 bg-pink-50',
    '樣式': 'border-indigo-300 bg-indigo-50',
    '配置': 'border-gray-300 bg-gray-50',
    '部署': 'border-orange-300 bg-orange-50',
    '合併MR': 'border-teal-300 bg-teal-50',
    '其他': 'border-gray-300 bg-gray-50',
    '未分類': 'border-gray-200 bg-gray-50'
  }
  return colors[category] || colors['未分類']
}
</script>
