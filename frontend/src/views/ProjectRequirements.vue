<template>
  <div class="requirements-page">
    <h2 class="page-title">项目需求</h2>

    <!-- 筛选条件卡片 -->
    <div class="filter-card">
      <div class="filter-card-title">
        <el-icon><Filter /></el-icon>
        <span>筛选条件</span>
      </div>
      <div class="filter-grid">
        <div class="filter-item">
          <label>财年</label>
          <el-select v-model="filters.fiscal_year" placeholder="选择财年" clearable>
            <el-option v-for="y in filterOptions.fiscal_years" :key="y" :label="y" :value="y" />
          </el-select>
        </div>

        <div class="filter-item">
          <label>Competency</label>
          <el-select v-model="filters.competency" placeholder="选择Competency" clearable>
            <el-option label="TC-Cyber Security" value="TC-Cyber Security" />
            <el-option label="TC-AI & Data" value="TC-AI & Data" />
            <el-option label="TC-Digital Engineering" value="TC-Digital Engineering" />
            <el-option label="TC-Platforms" value="TC-Platforms" />
            <el-option label="TC-Technology Strategy & Transformation" value="TC-Technology Strategy & Transformation" />
            <el-option label="BC-Business Transformation" value="BC-Business Transformation" />
            <el-option label="BC-Customer" value="BC-Customer" />
            <el-option label="BC-Finance" value="BC-Finance" />
            <el-option label="BC-Supply Chain & Operations" value="BC-Supply Chain & Operations" />
            <el-option label="RC-Digital Risk" value="RC-Digital Risk" />
            <el-option label="RC-Process & Controls" value="RC-Process & Controls" />
            <el-option label="RC-Regulatory Compliance" value="RC-Regulatory Compliance" />
            <el-option label="RC-Risk Management" value="RC-Risk Management" />
          </el-select>
        </div>

        <div class="filter-item">
          <label>所有机会</label>
          <el-select v-model="filters.project_type" placeholder="选择机会类型" clearable>
            <el-option v-for="t in filterOptions.project_types" :key="t" :label="t" :value="t" />
          </el-select>
        </div>

        <div class="filter-item">
          <label>技能</label>
          <el-select
            v-model="filters.skill"
            placeholder="选择技能"
            clearable
            filterable
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option v-for="s in filterOptions.skills" :key="s" :label="s" :value="s" />
          </el-select>
        </div>

        <div class="filter-item">
          <label>人数</label>
          <el-select v-model="filters.headcount_range" placeholder="选择人数范围" clearable>
            <el-option label="1-5人" value="1-5" />
            <el-option label="6-10人" value="6-10" />
            <el-option label="11-20人" value="11-20" />
            <el-option label="20人以上" value="20+" />
          </el-select>
        </div>

        <div class="filter-item">
          <label>Location</label>
          <el-select v-model="filters.location" placeholder="选择地点" clearable>
            <el-option v-for="l in filterOptions.locations" :key="l" :label="l" :value="l" />
          </el-select>
        </div>

        <div class="filter-item">
          <label>匹配状态</label>
          <el-select v-model="filters.match_status" placeholder="选择匹配状态" clearable>
            <el-option label="待满足" value="待满足" />
            <el-option label="关闭-Core满足" value="关闭-Core满足" />
            <el-option label="关闭·部分满足" value="关闭·部分满足" />
            <el-option label="关闭·未满足" value="关闭·未满足" />
            <el-option label="关闭-需求取消" value="关闭-需求取消" />
            <el-option label="关闭-需求重开" value="关闭-需求重开" />
            <el-option label="已满足" value="已满足" />
          </el-select>
        </div>

        <div class="filter-actions">
          <el-button class="reset-btn" @click="resetFilters">重置</el-button>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
        </div>
      </div>
    </div>

    <!-- 需求列表卡片 -->
    <div class="list-card">
      <div class="list-card-header">
        <span class="list-card-title">项目需求列表</span>
        <el-button type="primary" size="small">
          <el-icon><Plus /></el-icon>
          新增需求
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          :data="tableData"
          v-loading="loading"
          class="requirements-table"
          row-class-name="table-row"
          :element-loading-background="'rgba(10,22,40,0.8)'"
          style="min-width: 2100px"
        >
          <el-table-column prop="request_date" label="需求提出日期" width="130" />
          <el-table-column prop="requester" label="需求提出者" width="110" />
          <el-table-column prop="competency" label="Competency" width="120" />
          <el-table-column prop="project_type" label="项目类型" width="100" />
          <el-table-column prop="project_name" label="项目名称" min-width="160" />
          <el-table-column prop="ep_name" label="EP" width="100" />
          <el-table-column prop="em_name" label="EM" width="100" />

          <el-table-column label="项目时间" width="160">
            <template #default="{ row }">
              <span v-if="row.project_start_date || row.project_end_date">
                {{ formatYearMonth(row.project_start_date) }}-{{ formatYearMonth(row.project_end_date) }}
              </span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="技能" min-width="160">
            <template #default="{ row }">
              <div class="tag-list" v-if="row.required_skills">
                <el-tag
                  v-for="skill in row.required_skills.split(',')"
                  :key="skill"
                  size="small"
                  class="skill-tag"
                  effect="plain"
                >{{ skill.trim() }}</el-tag>
              </div>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="headcount" label="人数" width="70" />
          <el-table-column prop="description" label="详细要求" min-width="140" show-overflow-tooltip />
          <el-table-column prop="location" label="工作地点" width="100" />
          <el-table-column prop="job_content" label="工作内容" min-width="140" show-overflow-tooltip />

          <el-table-column label="匹配状态" width="130">
            <template #default="{ row }">
              <el-tag
                v-if="row.match_status"
                :type="getMatchStatusType(row.match_status)"
                size="small"
                effect="plain"
                class="status-tag"
              >{{ row.match_status }}</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="推荐顾问名单" min-width="160">
            <template #default="{ row }">
              <div class="tag-list" v-if="row.consultants && row.consultants.length">
                <el-tag
                  v-for="c in row.consultants"
                  :key="c.id"
                  size="small"
                  class="consultant-tag"
                  effect="plain"
                >{{ c.name }}</el-tag>
              </div>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <div class="action-row">
                <el-button size="small" type="primary" link>详情</el-button>
                <el-button size="small" type="primary" link class="delete-btn" @click="deleteRow(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar">
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { requirementApi } from '@/api/requirements'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const filters = reactive({
  fiscal_year: '',
  competency: '',
  project_type: '',
  skill: [],
  headcount_range: '',
  location: '',
  match_status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
})

const filterOptions = reactive({
  fiscal_years: [],
  competencies: [],
  project_types: [],
  locations: [],
  match_statuses: [],
  skills: [],
})

function formatYearMonth(dateStr) {
  if (!dateStr) return '?'
  // dateStr 格式为 "2024-01-15"，取前7位 "2024-01" 替换 "-" 为 "."
  return dateStr.slice(0, 7).replace('-', '.')
}

function getMatchStatusType(status) {
  const map = {
    '待满足': '',
    '已满足': 'success',
    '关闭-Core满足': 'success',
    '关闭·部分满足': 'warning',
    '关闭·未满足': 'danger',
    '关闭-需求取消': 'info',
    '关闭-需求重开': 'info',
  }
  return map[status] ?? 'info'
}

function handleFilter() {
  pagination.page = 1
  loadData()
}

function handleSizeChange() {
  pagination.page = 1
  loadData()
}

function resetFilters() {
  filters.fiscal_year = ''
  filters.competency = ''
  filters.project_type = ''
  filters.skill = []
  filters.headcount_range = ''
  filters.location = ''
  filters.match_status = ''
  pagination.page = 1
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...(filters.fiscal_year && { fiscal_year: filters.fiscal_year }),
      ...(filters.competency && { competency: filters.competency }),
      ...(filters.project_type && { project_type: filters.project_type }),
      ...(filters.skill.length && { skill: filters.skill }),
      ...(filters.headcount_range && { headcount_range: filters.headcount_range }),
      ...(filters.location && { location: filters.location }),
      ...(filters.match_status && { match_status: filters.match_status }),
    }
    const res = await requirementApi.list(params)
    tableData.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function loadFilterOptions() {
  try {
    const res = await requirementApi.getFilterOptions()
    Object.assign(filterOptions, res.data)
  } catch (e) {
    console.error(e)
  }
}

async function deleteRow(row) {
  try {
    await ElMessageBox.confirm(
      '确认删除该需求记录？此操作不可恢复。',
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await requirementApi.remove(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadFilterOptions()
  loadData()
})
</script>

<style scoped>
.requirements-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-cyan);
  letter-spacing: 0.5px;
}

/* 筛选条件卡片 */
.filter-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
}

.filter-card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-cyan);
  margin-bottom: 14px;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item label {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.filter-item .el-select {
  width: 160px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
  align-self: flex-end;
}

.reset-btn {
  border-color: var(--border-color) !important;
  color: var(--text-secondary) !important;
  background-color: transparent !important;
}

.reset-btn:hover {
  border-color: var(--accent-cyan) !important;
  color: var(--accent-cyan) !important;
}

/* 筛选下拉框背景色与表格背景一致，字体白色 */
.filter-card :deep(.el-select .el-input__wrapper),
.filter-card :deep(.el-select__wrapper) {
  background-color: var(--bg-card) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
  border-radius: 8px !important;
}

.filter-card :deep(.el-select .el-input__wrapper:hover),
.filter-card :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-cyan) inset !important;
}

.filter-card :deep(.el-select .el-input__inner),
.filter-card :deep(.el-select__placeholder),
.filter-card :deep(.el-select__selected-item span) {
  color: #ffffff !important;
}

.filter-card :deep(.el-select .el-input__suffix) {
  color: var(--text-secondary) !important;
}

/* 需求列表卡片 */
.list-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.list-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.list-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-cyan);
}

.table-wrapper {
  overflow: auto;
  flex: 1;
}

.requirements-table {
  min-width: 100%;
}

:deep(.table-row) {
  background-color: transparent !important;
}

:deep(.el-table__header-wrapper th) {
  background-color: rgba(0, 180, 220, 0.15) !important;
  color: #a8e6f0 !important;
}

:deep(.el-table__row:hover > td) {
  background-color: var(--bg-hover) !important;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.skill-tag {
  background-color: rgba(0, 170, 204, 0.1) !important;
  border-color: var(--accent-cyan-dim) !important;
  color: var(--accent-cyan) !important;
  font-size: 11px;
}

.consultant-tag {
  background-color: rgba(139, 195, 74, 0.1) !important;
  border-color: rgba(139, 195, 74, 0.4) !important;
  color: #8bc34a !important;
  font-size: 11px;
}

:deep(.status-tag.el-tag--plain) {
  border-radius: 4px;
  font-size: 12px;
}

:deep(.el-tag--plain) {
  background-color: rgba(0, 188, 212, 0.1) !important;
  border-color: var(--accent-cyan-dim) !important;
  color: var(--accent-cyan) !important;
}

:deep(.el-tag--success.el-tag--plain) {
  background-color: rgba(102, 187, 106, 0.1) !important;
  border-color: rgba(102, 187, 106, 0.5) !important;
  color: #66bb6a !important;
}

:deep(.el-tag--warning.el-tag--plain) {
  background-color: rgba(255, 167, 38, 0.1) !important;
  border-color: rgba(255, 167, 38, 0.5) !important;
  color: #ffa726 !important;
}

:deep(.el-tag--danger.el-tag--plain) {
  background-color: rgba(239, 83, 80, 0.1) !important;
  border-color: rgba(239, 83, 80, 0.5) !important;
  color: #ef5350 !important;
}

.text-muted {
  color: var(--text-muted);
}

.action-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.delete-btn {
  color: var(--accent-red) !important;
}

.delete-btn:hover {
  color: #ff6b6b !important;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.total-text {
  color: var(--text-muted);
  font-size: 13px;
  white-space: nowrap;
}
</style>
