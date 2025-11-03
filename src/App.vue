<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-gray-900">📊 工作進度追蹤系統</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- 篩選區 -->
      <div v-if="rawData" class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">🔍 篩選設定</h2>
          <!-- 快速篩選按鈕 -->
          <div class="flex gap-3">
            <button
              @click="setYesterdayFilter"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
              📅 昨日紀錄
            </button>
            <button
              @click="resetToDefault"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
            >
              🔄 還原
            </button>
          </div>
        </div>

        <!-- 專案類型篩選 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-3">專案類型</label>
          <div class="flex gap-3">
            <button
              @click="showSideProjects = false; applyFilter()"
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
              @click="showSideProjects = true; applyFilter()"
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
                @change="applyFilter"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-xs text-gray-600 mb-1">結束日期</label>
              <input
                type="date"
                v-model="filterEnd"
                @change="applyFilter"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 資料總覽 -->
      <div v-if="workData" class="space-y-6">
        <!-- 期間與作者 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-2xl font-bold mb-4">
            📈 您的工作成果（{{ workData.author }}）
          </h2>
          <p class="text-gray-600">{{ displayPeriod.start }} 至 {{ displayPeriod.end }}</p>
          <p class="text-sm text-gray-500 mt-1">
            共 {{ displayPeriod.days }} 天 ({{ displayPeriod.weeks }} 週)
          </p>
        </div>

        <!-- 統計卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">總提交次數</div>
            <div class="text-3xl font-bold text-blue-600">{{ displaySummary.totalCommits }}</div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">專案數量</div>
            <div class="text-3xl font-bold text-green-600">{{ displaySummary.projectCount }}</div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">日均提交</div>
            <div class="text-3xl font-bold text-purple-600">{{ displaySummary.dailyAverage }}</div>
          </div>
        </div>

        <!-- 智能彙總報告 -->
        <div v-for="project in analyzedProjects" :key="project.name" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-2xl font-bold mb-4">
            🎯 {{ project.name}} 專案成果（{{ project.totalCommits }} commits）
          </h3>

          <!-- 功能分組 -->
          <div v-for="(feature, idx) in project.features" :key="idx" class="mb-6">
            <h4 class="text-lg font-bold mb-3">
              {{ idx + 1 }}. {{ feature.name }} {{ feature.icon }}
              <span class="text-sm text-gray-500 font-normal">({{ feature.dateRange }})</span>
            </h4>
            <p class="text-sm text-gray-600 mb-3">{{ feature.totalCommits }} 次提交</p>

            <!-- 子分組 -->
            <div v-for="(subgroup, subIdx) in feature.subgroups" :key="subIdx" class="ml-4 mb-4">
              <h5 class="font-semibold text-gray-800 mb-2">
                {{ subgroup.name }}
                <span class="text-xs text-gray-500">({{ subgroup.dateRange }})</span>
              </h5>
              <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li v-for="(item, itemIdx) in subgroup.items" :key="itemIdx">
                  {{ item }}
                </li>
                <li v-if="subgroup.moreCount > 0" class="text-gray-500">
                  ... 以及其他 {{ subgroup.moreCount }} 項改進
                </li>
              </ul>
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

        <!-- Claude 效率對比 -->
        <div v-if="efficiencyData" class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg shadow-lg p-6 border-2 border-blue-200">
          <h3 class="text-2xl font-bold mb-6 text-gray-800">🚀 Claude AI 效率對比分析</h3>

          <!-- 期間對比卡片 -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div
              v-for="period in efficiencyData.periods"
              :key="period.period.id"
              class="bg-white rounded-lg p-5 shadow-md hover:shadow-lg transition-shadow"
            >
              <div class="text-sm font-semibold text-gray-600 mb-2">{{ period.period.name }}</div>
              <div class="text-3xl font-bold mb-1" :class="getPeriodColor(period.period.id)">
                {{ period.summary.dailyAverage }}
              </div>
              <div class="text-xs text-gray-500">commits/day</div>
              <div class="mt-3 pt-3 border-t border-gray-200 text-xs space-y-1">
                <div class="flex justify-between">
                  <span class="text-gray-600">總計</span>
                  <span class="font-semibold">{{ period.summary.totalCommits }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">天數</span>
                  <span class="font-semibold">{{ period.period.days }}天</span>
                </div>
                <div v-if="period.period.cost > 0" class="flex justify-between">
                  <span class="text-gray-600">成本</span>
                  <span class="font-semibold">${{ period.period.cost }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 效率提升統計 -->
          <div class="bg-white rounded-lg p-5 shadow-md">
            <h4 class="font-bold text-gray-800 mb-4">📈 效率提升趨勢</h4>
            <div class="space-y-3">
              <!-- 使用前（基準線） -->
              <div v-if="efficiencyData.periods.length > 0" class="flex items-center">
                <div class="w-32 text-sm font-medium text-gray-700">{{ efficiencyData.periods[0].period.name }}</div>
                <div class="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                  <div
                    class="h-full rounded-full flex items-center justify-end pr-2 bg-gray-400 text-white text-xs font-bold transition-all"
                    :style="{ width: getEfficiencyPercentage(efficiencyData.periods[0]) + '%' }"
                  >
                    基準線
                  </div>
                </div>
                <div class="w-24 text-right text-sm font-semibold text-gray-600">
                  {{ efficiencyData.periods[0].summary.dailyAverage }} /天
                </div>
              </div>

              <!-- 其他時期 -->
              <div v-for="(period, idx) in efficiencyData.periods.slice(1)" :key="idx" class="flex items-center">
                <div class="w-32 text-sm font-medium text-gray-700">{{ period.period.name }}</div>
                <div class="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                  <div
                    class="h-full rounded-full flex items-center justify-end pr-2 text-white text-xs font-bold transition-all"
                    :class="getEfficiencyBarColor(period.period.id)"
                    :style="{ width: getEfficiencyPercentage(period) + '%' }"
                  >
                    {{ getEfficiencyChange(period) }}
                  </div>
                </div>
                <div class="w-24 text-right text-sm font-semibold" :class="getPeriodColor(period.period.id)">
                  {{ period.summary.dailyAverage }} /天
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 載入中或無資料 -->
      <div v-else class="text-center py-12">
        <p class="text-gray-500">載入資料中...</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { groupCommitsByFeature, cleanCommitMessage } from './utils/analyzer.js'

const rawData = ref(null)
const workData = ref(null)
const filterStart = ref('')
const filterEnd = ref('')
const showSideProjects = ref(false)
const efficiencyData = ref(null)

// 設定預設日期範圍
const DEFAULT_START_DATE = '2025-10-30'
const getDefaultEndDate = () => dayjs().subtract(1, 'day').format('YYYY-MM-DD')

// 載入資料
onMounted(async () => {
  try {
    // 載入工作日誌
    const response = await fetch(import.meta.env.BASE_URL + 'data/work-log-latest.json')
    const data = await response.json()
    rawData.value = data
    workData.value = data

    // 設定預設篩選範圍
    filterStart.value = DEFAULT_START_DATE
    filterEnd.value = getDefaultEndDate()

    // 自動套用篩選
    applyFilter()

    // 載入效率對比數據
    const effResponse = await fetch(import.meta.env.BASE_URL + 'data/claude-efficiency-data.json')
    const effData = await effResponse.json()
    efficiencyData.value = effData
  } catch (error) {
    console.error('載入資料失敗：', error)
  }
})

// 設定昨日篩選
const setYesterdayFilter = () => {
  const yesterday = getDefaultEndDate()
  filterStart.value = yesterday
  filterEnd.value = yesterday
  applyFilter()
}

// 還原到預設日期
const resetToDefault = () => {
  filterStart.value = DEFAULT_START_DATE
  filterEnd.value = getDefaultEndDate()
  applyFilter()
}

// 套用篩選
const applyFilter = () => {
  if (!rawData.value) return

  const start = filterStart.value ? dayjs(filterStart.value) : null
  const end = filterEnd.value ? dayjs(filterEnd.value) : null

  const filteredProjects = rawData.value.projects
    .filter(project => {
      // 篩選專案類型
      if (!showSideProjects.value && project.type === 'side') {
        return false
      }
      return true
    })
    .map(project => {
      if (!project.commits) return project

      const filteredCommits = project.commits.filter(commit => {
        const commitDate = dayjs(commit.date)
        if (start && commitDate.isBefore(start, 'day')) return false
        if (end && commitDate.isAfter(end, 'day')) return false
        return true
      })

      return {
        ...project,
        commits: filteredCommits,
        totalCommits: filteredCommits.length
      }
    })
    .filter(p => p.totalCommits > 0)

  workData.value = {
    ...rawData.value,
    projects: filteredProjects
  }
}

// 顯示期間
const displayPeriod = computed(() => {
  if (!workData.value) return { start: '', end: '', days: 0, weeks: 0 }

  const start = filterStart.value || workData.value.period.start
  const end = filterEnd.value || workData.value.period.end

  const startDay = dayjs(start)
  const endDay = dayjs(end)
  const days = endDay.diff(startDay, 'day') + 1
  const weeks = Math.ceil(days / 7)

  return { start, end, days, weeks }
})

// 顯示統計
const displaySummary = computed(() => {
  if (!workData.value) return { totalCommits: 0, projectCount: 0, dailyAverage: 0 }

  const totalCommits = workData.value.projects.reduce((sum, p) => sum + p.totalCommits, 0)
  const projectCount = workData.value.projects.filter(p => p.totalCommits > 0).length

  const days = displayPeriod.value.days || 1
  const dailyAverage = (totalCommits / days).toFixed(1)

  return { totalCommits, projectCount, dailyAverage }
})

// 顯示專案（計算百分比）
const displayProjects = computed(() => {
  if (!workData.value) return []

  const total = displaySummary.value.totalCommits
  return workData.value.projects.map(p => ({
    ...p,
    percentage: total > 0 ? Math.round((p.totalCommits / total) * 100) : 0
  }))
})

// 分類統計
const categoryStats = computed(() => {
  if (!workData.value) return {}

  const stats = {}
  workData.value.projects.forEach(project => {
    if (!project.commits) return
    project.commits.forEach(commit => {
      const cat = commit.category || '未分類'
      stats[cat] = (stats[cat] || 0) + 1
    })
  })

  return stats
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
    '其他': 'border-gray-300 bg-gray-50',
    '未分類': 'border-gray-200 bg-gray-50'
  }
  return colors[category] || colors['未分類']
}

// 期間顏色
const getPeriodColor = (periodId) => {
  const colors = {
    'pre-claude': 'text-gray-600',
    'claude-standard': 'text-blue-600',
    'claude-max': 'text-purple-600',
    'claude-code': 'text-green-600'
  }
  return colors[periodId] || 'text-gray-600'
}

// 效率條顏色
const getEfficiencyBarColor = (periodId) => {
  const colors = {
    'claude-standard': 'bg-blue-500',
    'claude-max': 'bg-purple-500',
    'claude-code': 'bg-green-500'
  }
  return colors[periodId] || 'bg-gray-500'
}

// 計算效率提升百分比（用於長條圖寬度，基於最大值）
const getEfficiencyPercentage = (period) => {
  if (!efficiencyData.value || !efficiencyData.value.periods.length) return 0

  // 找出所有時期中日均最高的值
  const maxDaily = Math.max(...efficiencyData.value.periods.map(p => p.summary.dailyAverage))

  // 當前時期的日均值
  const current = period.summary.dailyAverage

  // 計算相對於最大值的百分比
  return (current / maxDaily) * 100
}

// 效率變化文字
const getEfficiencyChange = (period) => {
  if (!efficiencyData.value || !efficiencyData.value.periods.length) return ''
  const baseline = efficiencyData.value.periods[0].summary.dailyAverage
  const current = period.summary.dailyAverage
  const increase = Math.round(((current - baseline) / baseline) * 100)
  return increase > 0 ? `+${increase}%` : `${increase}%`
}

// 智能分析專案
const analyzedProjects = computed(() => {
  if (!workData.value) return []

  return workData.value.projects.map(project => {
    if (!project.commits || project.commits.length === 0) return null

    const { grouped, ungrouped } = groupCommitsByFeature(project.commits)

    const features = Object.values(grouped).map(feature => {
      const allCommits = [
        ...feature.commits,
        ...Object.values(feature.subgroups).flat()
      ]

      if (allCommits.length === 0) return null

      // 計算日期範圍
      const dates = allCommits.map(c => c.date).sort()
      const dateRange = dates.length > 1
        ? `${dates[0]} 至 ${dates[dates.length - 1]}`
        : dates[0]

      // 處理子分組
      const subgroups = Object.entries(feature.subgroups)
        .filter(([_, commits]) => commits.length > 0)
        .map(([name, commits]) => {
          const subDates = commits.map(c => c.date).sort()
          const subDateRange = subDates.length > 1
            ? `${subDates[0]} 至 ${subDates[subDates.length - 1]}`
            : subDates[0]

          const MAX_ITEMS = 5
          const items = commits.slice(0, MAX_ITEMS).map(c => cleanCommitMessage(c.message))
          const moreCount = Math.max(0, commits.length - MAX_ITEMS)

          return {
            name,
            dateRange: subDateRange,
            items,
            moreCount
          }
        })

      return {
        name: feature.name,
        icon: feature.icon,
        totalCommits: allCommits.length,
        dateRange,
        subgroups
      }
    }).filter(Boolean)

    // 如果有未分組的 commits，一併顯示
    if (ungrouped.length > 0) {
      const dates = ungrouped.map(c => c.date).sort()
      const dateRange = dates.length > 1
        ? `${dates[0]} 至 ${dates[dates.length - 1]}`
        : dates[0]

      const MAX_ITEMS = 10
      const items = ungrouped.slice(0, MAX_ITEMS).map(c => ({
        date: c.date,
        message: cleanCommitMessage(c.message)
      }))
      const moreCount = Math.max(0, ungrouped.length - MAX_ITEMS)

      features.push({
        name: features.length > 0 ? '其他變更' : '所有變更',
        icon: '📝',
        totalCommits: ungrouped.length,
        dateRange,
        subgroups: [{
          name: '近期提交',
          dateRange,
          items: items.map(i => `[${i.date}] ${i.message}`),
          moreCount
        }]
      })
    }

    return {
      name: project.name,
      totalCommits: project.totalCommits,
      features
    }
  }).filter(Boolean)
})
</script>
