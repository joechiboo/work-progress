<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex flex-wrap justify-between items-center gap-3 mb-1">
      <h3 class="text-xl font-bold">📈 提交趨勢</h3>
      <div class="flex gap-1 bg-gray-100 rounded-lg p-1">
        <button
          v-for="opt in granularityOptions"
          :key="opt.value"
          @click="granularity = opt.value"
          :class="[
            'px-3 py-1 text-sm rounded-md transition-colors',
            granularity === opt.value
              ? 'bg-white text-gray-900 shadow-sm font-semibold'
              : 'text-gray-600 hover:text-gray-900'
          ]"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>
    <p class="text-sm text-gray-500 mb-4">{{ subtitle }}</p>

    <div v-show="buckets.length" class="relative" style="height: 280px">
      <canvas ref="canvasEl"></canvas>
    </div>

    <p v-if="!buckets.length" class="text-center text-gray-400 py-12">
      這個區間沒有資料
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import dayjs from 'dayjs'
import Chart from 'chart.js/auto'

const props = defineProps({
  // [{ date, work, side, total }]，已依篩選區間裁切。
  // summary 只存有提交的日子，沒提交的日子在這個陣列裡是缺的。
  daily: { type: Array, required: true },
  // 篩選區間的頭尾；用來把沒提交的日子補成 0，時間軸才不會被壓縮
  rangeStart: { type: String, default: '' },
  rangeEnd: { type: String, default: '' },
  showSideProjects: { type: Boolean, default: false }
})

// 取自 dataviz palette 的 categorical slot 1 / 2（已跑過 validate_palette，全數通過）
const COLOR_WORK = '#2a78d6'
const COLOR_SIDE = '#eb6834'
const COLOR_AVG = '#52514e' // 移動平均是註解線，不是第三個分類，所以用文字灰

const canvasEl = ref(null)
let chart = null

const granularityOptions = [
  { value: 'auto', label: '自動' },
  { value: 'day', label: '日' },
  { value: 'week', label: '週' },
  { value: 'month', label: '月' }
]
const granularity = ref('auto')

// 區間頭尾：優先用篩選條件，沒給才退回資料本身的頭尾
const bounds = computed(() => {
  if (!props.daily.length) return null
  const start = props.rangeStart || props.daily[0].date
  const end = props.rangeEnd || props.daily[props.daily.length - 1].date
  return start <= end ? { start, end } : null
})

const spanDays = computed(() => {
  if (!bounds.value) return 0
  return dayjs(bounds.value.end).diff(dayjs(bounds.value.start), 'day') + 1
})

// 把有提交的日子補滿成連續日期，沒提交的補 0：
// 少掉的那幾天若整個不畫，時間軸會被壓縮，看起來像那段時間比較密集
const denseDaily = computed(() => {
  if (!bounds.value) return []
  const byDate = new Map(props.daily.map(d => [d.date, d]))
  const out = []
  let cur = dayjs(bounds.value.start)
  const last = dayjs(bounds.value.end)
  // 上限擋住手動輸入到離譜日期時跑出天文數字的迴圈
  for (let i = 0; !cur.isAfter(last, 'day') && i < 4000; i++) {
    const date = cur.format('YYYY-MM-DD')
    const hit = byDate.get(date)
    out.push({ date, work: hit?.work || 0, side: hit?.side || 0 })
    cur = cur.add(1, 'day')
  }
  return out
})

// 區間長度決定預設粒度：柱子太多就看不清楚
const effectiveGranularity = computed(() => {
  if (granularity.value !== 'auto') return granularity.value
  const days = spanDays.value
  if (days <= 62) return 'day'
  if (days <= 400) return 'week'
  return 'month'
})

// 把每日資料彙總成日 / 週 / 月的桶子
const buckets = computed(() => {
  const g = effectiveGranularity.value
  const map = new Map()

  for (const d of denseDaily.value) {
    const day = dayjs(d.date)
    let key, label
    if (g === 'day') {
      key = day.format('YYYY-MM-DD')
      label = day.format('MM/DD')
    } else if (g === 'week') {
      const monday = day.subtract((day.day() + 6) % 7, 'day')
      key = monday.format('YYYY-MM-DD')
      label = monday.format('MM/DD')
    } else {
      key = day.format('YYYY-MM')
      label = day.format('YYYY/MM')
    }
    if (!map.has(key)) map.set(key, { key, label, work: 0, side: 0 })
    const b = map.get(key)
    b.work += d.work
    b.side += d.side
  }

  return [...map.values()].sort((a, b) => (a.key < b.key ? -1 : 1))
})

// 移動平均視窗：日看 7、週看 4、月看 3
const avgWindow = computed(() => ({ day: 7, week: 4, month: 3 })[effectiveGranularity.value])

const movingAverage = computed(() => {
  const w = avgWindow.value
  const src = buckets.value.map(b => b.work + (props.showSideProjects ? b.side : 0))
  if (src.length < w) return null
  return src.map((_, i) => {
    if (i < w - 1) return null
    const slice = src.slice(i - w + 1, i + 1)
    return +(slice.reduce((s, v) => s + v, 0) / w).toFixed(1)
  })
})

const subtitle = computed(() => {
  const g = effectiveGranularity.value
  const unitName = { day: '每日', week: '每週', month: '每月' }[g]
  const bucketName = { day: '日', week: '週', month: '月' }[g]
  const auto = granularity.value === 'auto' ? '（依區間自動選用）' : ''
  const avg = movingAverage.value ? `，虛線為 ${avgWindow.value} ${bucketName}移動平均` : ''
  return `${unitName}提交數${auto}${avg}`
})

function fullLabel(idx) {
  const b = buckets.value[idx]
  if (!b) return ''
  const g = effectiveGranularity.value
  if (g === 'day') return dayjs(b.key).format('YYYY/MM/DD')
  if (g === 'week') return `${dayjs(b.key).format('YYYY/MM/DD')} 這一週`
  return dayjs(b.key + '-01').format('YYYY 年 M 月')
}

function render() {
  if (chart) { chart.destroy(); chart = null }
  if (!canvasEl.value || !buckets.value.length) return

  const labels = buckets.value.map(b => b.label)
  const datasets = [
    {
      type: 'bar',
      label: '工作專案',
      data: buckets.value.map(b => b.work),
      backgroundColor: COLOR_WORK,
      borderRadius: 4,
      borderSkipped: 'bottom',
      stack: 'commits',
      pointStyle: 'rectRounded'
    }
  ]

  if (props.showSideProjects) {
    // 堆疊段之間留 2px 底色縫
    datasets[0].borderWidth = { top: 2 }
    datasets[0].borderColor = '#ffffff'
    datasets.push({
      type: 'bar',
      label: 'Side Projects',
      data: buckets.value.map(b => b.side),
      backgroundColor: COLOR_SIDE,
      borderRadius: 4,
      borderSkipped: 'bottom',
      stack: 'commits',
      pointStyle: 'rectRounded'
    })
  }

  if (movingAverage.value) {
    datasets.push({
      type: 'line',
      label: `${avgWindow.value} 期移動平均`,
      data: movingAverage.value,
      borderColor: COLOR_AVG,
      borderWidth: 2,
      borderDash: [5, 4],
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.3,
      spanGaps: false,
      pointStyle: 'line'
    })
  }

  chart = new Chart(canvasEl.value, {
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 250 },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { usePointStyle: true, boxWidth: 12, padding: 16 }
        },
        tooltip: {
          backgroundColor: 'rgba(17,17,17,0.92)',
          padding: 10,
          callbacks: {
            title: items => fullLabel(items[0].dataIndex),
            footer: items => {
              const bars = items.filter(i => i.dataset.type === 'bar')
              if (bars.length < 2) return ''
              return `合計 ${bars.reduce((s, i) => s + i.parsed.y, 0)} commits`
            }
          }
        }
      },
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          ticks: { color: '#52514e', autoSkip: true, maxRotation: 0, maxTicksLimit: 12 },
          border: { color: '#e5e5e2' }
        },
        y: {
          stacked: true,
          beginAtZero: true,
          grid: { color: '#f0efec' },
          ticks: { color: '#52514e', precision: 0 },
          border: { display: false }
        }
      }
    }
  })
}

onMounted(render)
onBeforeUnmount(() => { if (chart) chart.destroy() })
watch(
  [buckets, movingAverage, () => props.showSideProjects],
  () => nextTick(render)
)
</script>
