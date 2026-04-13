<template>
  <div class="employees-page">
    <!-- 左侧主区域 -->
    <div class="main-area">
      <h2 class="page-title">员工列表</h2>

      <!-- 筛选栏 + 表格 大框 -->
      <div class="list-card">

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索姓名或GPN"
          class="filter-search"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="filters.competency"
          placeholder="选择部门"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option v-for="c in filterOptions.competencies" :key="c" :label="c" :value="c" />
        </el-select>

        <el-select
          v-model="filters.grade"
          placeholder="选择职级"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option v-for="g in filterOptions.grades" :key="g" :label="g" :value="g" />
        </el-select>

        <el-select
          v-model="filters.skill"
          placeholder="选择技能"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option v-for="s in filterOptions.skills" :key="s" :label="s" :value="s" />
        </el-select>

        <el-select
          v-model="filters.status"
          placeholder="选择状态"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option v-for="s in filterOptions.statuses" :key="s" :label="s" :value="s" />
        </el-select>

        <el-button class="refresh-btn" @click="loadData">
          <el-icon><RefreshRight /></el-icon>
          刷新
        </el-button>
        <el-button class="add-btn" type="primary" size="small" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          :data="tableData"
          v-loading="loading"
          class="employee-table"
          row-class-name="table-row"
          @sort-change="handleSortChange"
          :element-loading-background="'rgba(10,22,40,0.8)'"
          style="min-width: 1200px"
        >
          <el-table-column prop="name" label="姓名" width="100">
            <template #default="{ row }">
              <router-link :to="`/employees/${row.id}`" class="name-link">
                {{ row.name }}
              </router-link>
            </template>
          </el-table-column>

          <el-table-column prop="gpn" label="GPN" width="130" />

          <el-table-column prop="competency" label="Competency" min-width="130">
            <template #default="{ row }">
              <el-input
                v-if="editingId === row.id"
                v-model="editRow.competency"
                size="small"
              />
              <span v-else>{{ row.competency || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="grade" label="职级" width="110">
            <template #default="{ row }">
              <el-select
                v-if="editingId === row.id"
                v-model="editRow.grade"
                size="small"
              >
                <el-option v-for="g in filterOptions.grades" :key="g" :label="g" :value="g" />
              </el-select>
              <span v-else-if="row.grade" class="grade-badge">{{ row.grade }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column prop="location" label="Location" width="130">
            <template #default="{ row }">
              <el-input
                v-if="editingId === row.id"
                v-model="editRow.location"
                size="small"
              />
              <span v-else>{{ row.location || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="counsellor_name" label="Counsellor" width="120">
            <template #default="{ row }">
              <span class="counsellor-text">{{ row.counsellor_name || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column label="当前支持项目" min-width="160">
            <template #default="{ row }">
              <router-link
                v-if="row.current_project"
                :to="`/projects`"
                class="project-link"
              >
                {{ row.current_project.name }}
              </router-link>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="ytd_ut" label="YTD UT" width="110" sortable="custom">
            <template #default="{ row }">
              <el-input
                v-if="editingId === row.id"
                v-model.number="editRow.ytd_ut"
                size="small"
                type="number"
                :min="0"
                :max="100"
              />
              <span v-else :class="getUtClass(row.ytd_ut)">
                {{ row.ytd_ut != null ? row.ytd_ut.toFixed(1) + '%' : '-' }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-select
                v-if="editingId === row.id"
                v-model="editRow.status"
                size="small"
              >
                <el-option v-for="s in filterOptions.statuses" :key="s" :label="s" :value="s" />
              </el-select>
              <el-tag
                v-else-if="row.status"
                :type="getStatusType(row.status)"
                size="small"
                class="status-tag"
                effect="plain"
              >{{ row.status }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <template v-if="editingId === row.id">
                <div class="action-cell">
                  <div class="action-row">
                    <el-button size="small" type="primary" link @click="saveRow(row)">保存</el-button>
                    <el-button size="small" link @click="cancelEdit">取消</el-button>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="action-cell">
                  <div class="action-row">
                    <el-button size="small" type="primary" link @click="startEdit(row)">编辑</el-button>
                    <el-button size="small" type="primary" link @click="$router.push(`/employees/${row.id}`)">查看</el-button>
                  </div>
                  <div class="action-row">
                    <el-button size="small" type="primary" link class="delete-btn" @click="deleteRow(row)">删除</el-button>
                  </div>
                </div>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar">
        <el-button
          class="export-btn"
          size="small"
          @click="handleExport"
          :loading="exporting"
        >
          <el-icon><Download /></el-icon>
          导出 Excel
        </el-button>
        <div class="pagination-right">
          <span class="total-text">共 {{ total }} 条记录</span>
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="total"
            layout="prev, pager, next, sizes"
            @current-change="loadData"
            @size-change="handleSizeChange"
          />
        </div>
      </div>

      </div> <!-- /list-card -->

      <!-- 新增员工弹窗 -->
      <el-dialog v-model="addDialogVisible" title="新增员工" width="400px" :close-on-click-modal="false" class="add-employee-dialog">
        <el-form :model="addForm" label-width="90px" size="small" style="--el-form-item-mb: 12px">
          <el-form-item label="GPN" required>
            <el-input v-model="addForm.gpn" placeholder="请输入GPN" />
          </el-form-item>
          <el-form-item label="姓名" required>
            <el-input v-model="addForm.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="Competency">
            <el-select v-model="addForm.competency" placeholder="选择部门" clearable style="width:100%">
              <el-option v-for="c in filterOptions.competencies" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="职级">
            <el-select v-model="addForm.grade" placeholder="选择职级" clearable style="width:100%">
              <el-option v-for="g in filterOptions.grades" :key="g" :label="g" :value="g" />
            </el-select>
          </el-form-item>
          <el-form-item label="Location">
            <el-select v-model="addForm.location" placeholder="选择城市" clearable style="width:100%">
              <el-option v-for="l in filterOptions.locations" :key="l" :label="l" :value="l" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="addForm.status" style="width:100%" @change="addForm.project_id = null">
              <el-option v-for="s in filterOptions.statuses" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="addForm.status === '在项'" label="当前项目">
            <el-select v-model="addForm.project_id" placeholder="选择项目" clearable filterable style="width:100%">
              <el-option
                v-for="p in filterOptions.projects"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Counsellor">
            <el-select v-model="addForm.counsellor_id" placeholder="选择上级" clearable filterable style="width:100%">
              <el-option
                v-for="emp in allEmployees"
                :key="emp.id"
                :label="`${emp.name} (${emp.grade || '-'})`"
                :value="emp.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="addForm.email" placeholder="请输入邮箱" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="addLoading" @click="submitAdd">确认新增</el-button>
        </template>
      </el-dialog>
    </div>

    <!-- 右侧面板 -->
    <div class="right-panel">
      <!-- 技能分布 -->
      <div class="panel-card">
        <div class="panel-title">技能分布</div>
        <v-chart class="skill-chart" :option="skillChartOption" autoresize />
      </div>

      <!-- 快速统计 -->
      <div class="panel-card">
        <div class="panel-title">快速统计</div>
        <div class="stat-list">
          <div class="stat-item">
            <span class="stat-label">在职员工</span>
            <span class="stat-value cyan">{{ stats.total }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">在项</span>
            <span class="stat-value green">{{ stats.onProject }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Bench</span>
            <span class="stat-value orange">{{ stats.bench }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">休假</span>
            <span class="stat-value muted">{{ stats.leave }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { employeeApi } from '@/api/employees'

use([PieChart, TooltipComponent, LegendComponent, CanvasRenderer])

const loading = ref(false)
const exporting = ref(false)
const tableData = ref([])
const editingId = ref(null)
const editRow = reactive({})
const addDialogVisible = ref(false)
const addLoading = ref(false)
const addForm = reactive({
  gpn: '', name: '', competency: '', grade: '', location: '',
  status: 'bench', email: '', counsellor_id: null, project_id: null,
})
const allEmployees = ref([])
const total = ref(0)

const filters = reactive({
  keyword: '',
  competency: '',
  grade: '',
  skill: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
})

const filterOptions = reactive({
  competencies: [],
  grades: [],
  locations: [],
  skills: [],
  statuses: [],
  projects: [],
})

const stats = reactive({
  total: 0,
  onProject: 0,
  bench: 0,
  leave: 0,
})

// 技能分布图表配置
const skillChartOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: '#0f2744',
    borderColor: '#1a3a5c',
    textStyle: { color: '#e0f0ff' },
  },
  legend: {
    orient: 'vertical',
    left: 0,
    top: 'center',
    textStyle: { color: '#8ab4d4', fontSize: 12 },
    itemWidth: 14,
    itemHeight: 14,
    itemGap: 10,
  },
  series: [
    {
      type: 'pie',
      radius: ['45%', '72%'],
      center: ['65%', '50%'],
      data: [],
      label: { show: false },
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,212,255,0.3)' },
      },
    },
  ],
})

const skillColors = ['#7c6fcd', '#8bc34a', '#ffc107', '#ef5350', '#26c6da', '#ff7043', '#ab47bc']

let searchTimer = null

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadData()
  }, 400)
}

function handleFilter() {
  pagination.page = 1
  loadData()
}

function handleSizeChange() {
  pagination.page = 1
  loadData()
}

function handleSortChange() {
  loadData()
}

function getStatusType(status) {
  const map = { '在项': '', 'bench': 'info', '休假': 'warning' }
  return map[status] ?? 'info'
}

function getUtClass(ut) {
  if (ut == null) return 'text-muted'
  if (ut >= 85) return 'ut-high'
  if (ut >= 70) return 'ut-mid'
  return 'ut-low'
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...(filters.keyword && { keyword: filters.keyword }),
      ...(filters.competency && { competency: filters.competency }),
      ...(filters.grade && { grade: filters.grade }),
      ...(filters.skill && { skill: filters.skill }),
      ...(filters.status && { status: filters.status }),
    }
    const res = await employeeApi.list(params)
    tableData.value = res.data.items
    total.value = res.data.total

    // 更新统计
    stats.total = res.data.total
    stats.onProject = res.data.items.filter(e => e.status === '在项').length
    stats.bench = res.data.items.filter(e => e.status === 'bench').length
    stats.leave = res.data.items.filter(e => e.status === '休假').length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadFilterOptions() {
  try {
    const res = await employeeApi.getFilterOptions()
    Object.assign(filterOptions, res.data)
    // 更新技能分布图
    const skillData = res.data.skills.slice(0, 7).map((s, i) => ({
      name: s,
      value: Math.floor(Math.random() * 30 + 5),
      itemStyle: { color: skillColors[i % skillColors.length] },
    }))
    skillChartOption.value.series[0].data = skillData
    skillChartOption.value.legend.data = skillData.map(s => s.name)
  } catch (e) {
    console.error(e)
  }
}

function startEdit(row) {
  editingId.value = row.id
  Object.assign(editRow, {
    competency: row.competency,
    grade: row.grade,
    location: row.location,
    ytd_ut: row.ytd_ut,
    status: row.status,
  })
}

function cancelEdit() {
  editingId.value = null
}

async function saveRow(row) {
  try {
    await employeeApi.update(row.id, {
      competency: editRow.competency,
      grade: editRow.grade,
      location: editRow.location,
      ytd_ut: editRow.ytd_ut,
      status: editRow.status,
    })
    // 直接更新本地数据，不需要重新请求
    Object.assign(row, {
      competency: editRow.competency,
      grade: editRow.grade,
      location: editRow.location,
      ytd_ut: editRow.ytd_ut,
      status: editRow.status,
    })
    editingId.value = null
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function openAddDialog() {
  Object.assign(addForm, { gpn: '', name: '', competency: '', grade: '', location: '', status: 'bench', email: '', counsellor_id: null, project_id: null })
  addDialogVisible.value = true
  // 加载全部员工供 Counsellor 选择（异步，不阻塞弹窗打开）
  if (allEmployees.value.length === 0) {
    try {
      const res = await employeeApi.list({ page: 1, page_size: 999 })
      allEmployees.value = res.data.items
    } catch (e) {
      console.error('加载员工列表失败', e)
    }
  }
}

async function submitAdd() {
  if (!addForm.gpn || !addForm.name) {
    ElMessage.warning('GPN 和姓名为必填项')
    return
  }
  addLoading.value = true
  try {
    await employeeApi.create({ ...addForm, ytd_ut: 0 })
    addDialogVisible.value = false
    ElMessage.success('新增成功')
    loadData()
  } catch (e) {
    ElMessage.error('新增失败，GPN 可能已存在')
  } finally {
    addLoading.value = false
  }
}

async function deleteRow(row) {
  try {
    await ElMessageBox.confirm(`确认删除员工「${row.name}」？此操作不可恢复。`, '删除确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await employeeApi.remove(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const params = {
      ...(filters.keyword && { keyword: filters.keyword }),
      ...(filters.competency && { competency: filters.competency }),
      ...(filters.grade && { grade: filters.grade }),
      ...(filters.skill && { skill: filters.skill }),
      ...(filters.status && { status: filters.status }),
    }
    const res = await employeeApi.exportExcel(params)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'employees.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadFilterOptions()
  loadData()
})
</script>

<style scoped>
.employees-page {
  display: flex;
  gap: 20px;
  height: 100%;
}

.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-cyan);
  letter-spacing: 0.5px;
}

/* 大框：筛选栏 + 表格 + 分页 */
.list-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
}

.filter-search {
  width: 200px;
}

.filter-select {
  width: 140px;
}

.refresh-btn {
  margin-left: auto;
  border-color: var(--border-color) !important;
  color: var(--text-secondary) !important;
  background-color: transparent !important;
}

.refresh-btn:hover {
  border-color: var(--accent-cyan) !important;
  color: var(--accent-cyan) !important;
}

.add-btn {
  margin-left: 4px;
}

/* 表格 */
.table-wrapper {
  overflow: auto;
  flex: 1;
}

.employee-table {
  width: 100%;
}

:deep(.table-row) {
  background-color: transparent !important;
}

:deep(.el-table__row:hover > td) {
  background-color: var(--bg-hover) !important;
}

.name-link {
  color: var(--accent-cyan);
  text-decoration: none;
  font-weight: 500;
}

.name-link:hover {
  text-decoration: underline;
}

.grade-badge {
  display: inline-block;
  padding: 2px 10px;
  background-color: rgba(0, 170, 204, 0.15);
  border: 1px solid var(--accent-cyan-dim);
  border-radius: 4px;
  color: var(--accent-cyan);
  font-size: 12px;
  font-weight: 600;
}

.project-link {
  color: #64b5f6;
  text-decoration: none;
  font-size: 13px;
}

.project-link:hover {
  text-decoration: underline;
}

.counsellor-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.action-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 2px 0;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 0;
}

.action-row .el-button + .el-button {
  margin-left: 6px;
}

.delete-btn {
  color: var(--accent-red) !important;
}

.delete-btn:hover {
  color: #ff6b6b !important;
}

.text-muted {
  color: var(--text-muted);
}

.ut-high { color: var(--accent-green); font-weight: 600; }
.ut-mid  { color: var(--accent-orange); font-weight: 600; }
.ut-low  { color: var(--accent-red); font-weight: 600; }

:deep(.status-tag.el-tag--plain) {
  border-radius: 4px;
  font-size: 12px;
}

:deep(.el-tag--plain) {
  background-color: rgba(0, 188, 212, 0.1) !important;
  border-color: var(--status-on-project) !important;
  color: var(--status-on-project) !important;
}

:deep(.el-tag--info.el-tag--plain) {
  background-color: rgba(120, 144, 156, 0.1) !important;
  border-color: var(--status-bench) !important;
  color: var(--status-bench) !important;
}

:deep(.el-tag--warning.el-tag--plain) {
  background-color: rgba(171, 71, 188, 0.1) !important;
  border-color: var(--status-leave) !important;
  color: var(--status-leave) !important;
}

/* 分页 */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.pagination-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-text {
  color: var(--text-muted);
  font-size: 13px;
  white-space: nowrap;
}

.export-btn {
  border-color: var(--accent-cyan-dim) !important;
  color: var(--accent-cyan) !important;
  background-color: transparent !important;
}

.export-btn:hover {
  background-color: var(--accent-cyan) !important;
  color: var(--bg-primary) !important;
}

/* 右侧面板 */
.right-panel {
  width: 260px;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 44px;
}

.panel-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-cyan);
  margin-bottom: 12px;
}

.skill-chart {
  height: 200px;
  width: 100%;
}

.stat-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.stat-value.cyan  { color: var(--accent-cyan); }
.stat-value.green { color: var(--accent-green); }
.stat-value.orange { color: var(--accent-orange); }
.stat-value.muted { color: var(--text-muted); }
</style>
