<template>
  <div v-if="data" class="space-y-6">
    <!-- 標題與資料範圍 -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex flex-wrap justify-between items-start gap-4">
        <div>
          <h2 class="text-2xl font-bold mb-2">🚀 AI 效益評估</h2>
          <p class="text-gray-600 text-sm">
            資料區間：{{ data.dataRange.start }} ~ {{ data.dataRange.end }}
            （{{ data.dataRange.days }} 天，其中 {{ data.overall.aiDays }} 天有 AI 訂閱）
          </p>
        </div>
        <div class="text-right text-xs text-gray-500">
          <div>重算日期：{{ data.generatedAt }}</div>
          <div>資料來源：{{ data.source }}</div>
        </div>
      </div>
    </div>

    <!-- 總覽數字 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 mb-2">累計投入</div>
        <div class="text-2xl font-bold text-red-600">US$ {{ fmt(data.overall.totalCost) }}</div>
        <div class="text-xs text-gray-500 mt-1">≈ NT$ {{ fmt(data.overall.totalCostTwd) }}（{{ data.overall.aiDays }} 天）</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 mb-2">AI 期間產出</div>
        <div class="text-2xl font-bold text-blue-600">{{ fmt(data.overall.aiCommits) }} commits</div>
        <div class="text-xs text-gray-500 mt-1">工作 {{ fmt(data.overall.aiWorkCommits) }} ｜ Side {{ fmt(data.overall.aiCommits - data.overall.aiWorkCommits) }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 mb-2">每 commit 成本</div>
        <div class="text-2xl font-bold text-purple-600">NT$ {{ data.overall.costPerCommitTwd }}</div>
        <div class="text-xs text-gray-500 mt-1">日均成本 NT$ {{ data.overall.dailyCostTwd }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 mb-2">回本門檻</div>
        <div class="text-2xl font-bold text-green-600">{{ data.overall.breakEvenHours }} 小時/月</div>
        <div class="text-xs text-gray-500 mt-1">月費 NT$ {{ fmt(data.overall.monthlyCostTwd) }} ÷ 時薪 NT$ {{ data.assumptions.hourlyTwd }}</div>
      </div>
    </div>

    <!-- 分期比較表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-xl font-bold mb-1">📊 分期比較</h3>
      <p class="text-sm text-gray-500 mb-4">以「使用前」為基準線，四個訂閱階段的實際產出與成本</p>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 text-gray-700">
              <th class="text-left py-2 px-3 font-semibold">階段</th>
              <th class="text-right py-2 px-3 font-semibold">天數</th>
              <th class="text-right py-2 px-3 font-semibold">總 commits</th>
              <th class="text-right py-2 px-3 font-semibold">工作 / Side</th>
              <th class="text-right py-2 px-3 font-semibold">日均</th>
              <th class="text-right py-2 px-3 font-semibold">工作日均</th>
              <th class="text-right py-2 px-3 font-semibold">vs 基準（工作）</th>
              <th class="text-right py-2 px-3 font-semibold">有產出天數</th>
              <th class="text-right py-2 px-3 font-semibold">費用</th>
              <th class="text-right py-2 px-3 font-semibold">每 commit</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in data.periods" :key="p.id" class="border-b last:border-b-0 hover:bg-gray-50">
              <td class="py-2 px-3">
                <div class="font-semibold" :class="periodColor(p.id)">{{ p.name }}</div>
                <div class="text-xs text-gray-500">{{ p.start }} ~ {{ p.end }}</div>
                <div class="text-xs text-gray-400">{{ p.plan }}</div>
              </td>
              <td class="text-right py-2 px-3">{{ p.days }}</td>
              <td class="text-right py-2 px-3 font-semibold">{{ fmt(p.totalCommits) }}</td>
              <td class="text-right py-2 px-3 text-gray-600">{{ fmt(p.workCommits) }} / {{ fmt(p.sideCommits) }}</td>
              <td class="text-right py-2 px-3">{{ p.dailyAverage }}</td>
              <td class="text-right py-2 px-3 font-semibold">{{ p.workDailyAverage }}</td>
              <td class="text-right py-2 px-3">
                <span v-if="p.workLift === null" class="text-gray-400">基準線</span>
                <span v-else class="font-semibold text-green-600">+{{ p.workLift }}%</span>
              </td>
              <td class="text-right py-2 px-3">{{ p.activeDays }}/{{ p.days }}<span class="text-gray-400 text-xs">（{{ p.activeRatio }}%）</span></td>
              <td class="text-right py-2 px-3">
                <div>US$ {{ fmt(p.cost) }}</div>
                <div class="text-xs text-gray-400">NT$ {{ fmt(p.costTwd) }}</div>
              </td>
              <td class="text-right py-2 px-3">
                <span v-if="p.costPerCommit">NT$ {{ (p.costPerCommit * data.assumptions.usdTwd).toFixed(1) }}</span>
                <span v-else class="text-gray-400">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 工作 commits 日均對比 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-xl font-bold mb-1">📈 工作專案日均產出</h3>
      <p class="text-sm text-gray-500 mb-4">只看公司專案（排除 side project），這是對工作產出最直接的指標</p>
      <div class="space-y-3">
        <div v-for="p in data.periods" :key="p.id" class="flex items-center gap-3">
          <div class="w-28 shrink-0 text-sm font-medium text-gray-700">{{ p.name }}</div>
          <div class="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
            <div
              class="h-full rounded-full flex items-center justify-end pr-2 text-white text-xs font-bold"
              :class="barColor(p.id)"
              :style="{ width: barWidth(p.workDailyAverage) + '%' }"
            >
              {{ p.workLift === null ? '基準線' : '+' + p.workLift + '%' }}
            </div>
          </div>
          <div class="w-20 text-right text-sm font-semibold" :class="periodColor(p.id)">{{ p.workDailyAverage }} /天</div>
        </div>
      </div>
    </div>

    <!-- 月度趨勢 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-xl font-bold mb-1">🗓️ 月度產出趨勢</h3>
      <p class="text-sm text-gray-500 mb-4">
        深色為工作專案、淺色為 side project；數字為該月總 commits
        <span v-if="lastMonthPartial" class="text-amber-600">（{{ data.monthly[data.monthly.length - 1].month }} 僅計至 {{ data.dataRange.end }}）</span>
      </p>
      <div class="overflow-x-auto">
        <div class="flex items-end gap-2 min-w-[640px] h-56">
          <div v-for="m in data.monthly" :key="m.month" class="flex-1 flex flex-col items-center justify-end h-full">
            <div class="text-xs text-gray-600 mb-1">{{ m.total }}</div>
            <div class="w-full flex flex-col justify-end" :style="{ height: monthHeight(m.total) + '%' }">
              <div class="w-full bg-blue-200 rounded-t" :style="{ height: pct(m.side, m.total) + '%' }"></div>
              <div class="w-full bg-blue-600" :style="{ height: pct(m.work, m.total) + '%' }"></div>
            </div>
            <div class="text-[10px] text-gray-500 mt-1 whitespace-nowrap">{{ m.month.slice(2) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 口徑與限制 -->
    <div class="bg-amber-50 border-l-4 border-amber-400 rounded-lg p-6">
      <h3 class="font-bold text-gray-800 mb-3">📌 口徑與限制</h3>
      <ul class="text-sm text-gray-700 space-y-2 list-disc pl-5">
        <li><strong>commit 數是活動量，不等於價值。</strong>commit 顆粒度會隨習慣改變（AI 輔助後傾向小步提交），跨期間比較會高估提升幅度，這裡同時列出「有產出天數」作為佐證指標。</li>
        <li><strong>總量提升有很大一部分來自 side project。</strong>使用前 side 只佔 {{ data.periods[0].sideCommits }} 筆，之後大幅增加；因此主指標採「工作專案日均」而非總量。</li>
        <li><strong>回本門檻是唯一的金額推論。</strong>月費 NT$ {{ fmt(data.overall.monthlyCostTwd) }}，以時薪 NT$ {{ data.assumptions.hourlyTwd }} 計，每月省下 {{ data.overall.breakEvenHours }} 小時即打平；不再換算「時間價值 / ROI 倍數」這類無法驗證的數字。</li>
        <li>{{ data.assumptions.note }}</li>
      </ul>
    </div>

    <!-- 費用明細 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-xl font-bold mb-4">💳 訂閱費用明細</h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 text-gray-700">
              <th class="text-left py-2 px-3 font-semibold">扣款日</th>
              <th class="text-left py-2 px-3 font-semibold">方案</th>
              <th class="text-right py-2 px-3 font-semibold">金額</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in data.billing" :key="b.date" class="border-b last:border-b-0 hover:bg-gray-50">
              <td class="py-2 px-3 text-gray-600">{{ b.date }}</td>
              <td class="py-2 px-3">{{ b.plan }}</td>
              <td class="text-right py-2 px-3 font-semibold">US$ {{ b.amount.toFixed(2) }}</td>
            </tr>
            <tr class="bg-blue-50 font-bold">
              <td class="py-2 px-3" colspan="2">合計</td>
              <td class="text-right py-2 px-3 text-red-600">US$ {{ fmt(data.overall.totalCost) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-12">
    <p class="text-gray-500">載入效益資料中...</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: null }
})

const fmt = (n) => (n === null || n === undefined ? '—' : Number(n).toLocaleString('en-US'))

const periodColor = (id) => ({
  'pre-claude': 'text-gray-600',
  'claude-pro': 'text-blue-600',
  'claude-max-1': 'text-purple-600',
  'claude-max-2': 'text-green-600'
}[id] || 'text-gray-600')

const barColor = (id) => ({
  'pre-claude': 'bg-gray-400',
  'claude-pro': 'bg-blue-500',
  'claude-max-1': 'bg-purple-500',
  'claude-max-2': 'bg-green-500'
}[id] || 'bg-gray-400')

const maxWorkDaily = computed(() => {
  if (!props.data) return 1
  return Math.max(...props.data.periods.map(p => p.workDailyAverage))
})

const barWidth = (value) => Math.max(8, Math.round((value / maxWorkDaily.value) * 100))

const maxMonthTotal = computed(() => {
  if (!props.data) return 1
  return Math.max(...props.data.monthly.map(m => m.total))
})

const monthHeight = (total) => Math.max(3, Math.round((total / maxMonthTotal.value) * 100))

const pct = (part, total) => (total ? (part / total) * 100 : 0)

const lastMonthPartial = computed(() => {
  if (!props.data) return false
  const last = props.data.monthly[props.data.monthly.length - 1]
  return last.days < 28
})
</script>
