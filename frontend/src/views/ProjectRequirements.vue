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
        <el-button type="primary" size="small" @click="openCreateDialog">
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
          <el-table-column label="项目类型" width="110">
            <template #default="{ row }">
              <el-tag v-if="row.project_type" size="small" class="skill-tag" effect="plain">
                {{ row.project_type }}
              </el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="opportunity_type" label="所有机会" width="90" />
          <el-table-column label="项目名称" min-width="160">
            <template #default="{ row }">
              <span v-if="row.project_name" class="project-name-cell">{{ row.project_name }}</span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
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
                <el-button size="small" type="primary" link @click="openDetailDialog(row)">详情</el-button>
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

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="项目需求详情"
      width="600px"
      :close-on-click-modal="false"
      :teleported="false"
      class="detail-dialog"
    >
      <div class="detail-form">
        <div class="detail-grid">
          <div class="detail-field">
            <label>项目名字</label>
            <el-input v-model="detailForm.project_name" />
          </div>
          <div class="detail-field">
            <label>Competency</label>
            <el-select v-model="detailForm.competency" placeholder="请选择" clearable style="width:100%">
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

          <div class="detail-field">
            <label>需求提出者</label>
            <el-select v-model="detailForm.requester" placeholder="请选择" clearable filterable style="width:100%">
              <el-option v-for="e in employeeList" :key="e.id" :label="e.name" :value="e.name" />
            </el-select>
          </div>
          <div class="detail-field">
            <label>需求提出日期</label>
            <el-date-picker v-model="detailForm.request_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
          </div>

          <div class="detail-field">
            <label>EP</label>
            <el-select v-model="detailForm.ep_id" placeholder="请选择EP" clearable filterable style="width:100%">
              <el-option v-for="e in epList" :key="e.id" :label="e.name" :value="e.id" />
            </el-select>
          </div>
          <div class="detail-field">
            <label>EM</label>
            <el-select v-model="detailForm.em_id" placeholder="请选择EM" clearable filterable style="width:100%">
              <el-option v-for="e in emList" :key="e.id" :label="e.name" :value="e.id" />
            </el-select>
          </div>

          <div class="detail-field">
            <label>项目开始时间</label>
            <el-date-picker v-model="detailForm.project_start_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
          </div>
          <div class="detail-field">
            <label>项目结束时间</label>
            <el-date-picker v-model="detailForm.project_end_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
          </div>

          <div class="detail-field">
            <label>人数</label>
            <el-input v-model.number="detailForm.headcount" type="number" :min="1" />
          </div>
          <div class="detail-field">
            <label>所有机会</label>
            <el-select v-model="detailForm.opportunity_type" placeholder="请选择" clearable style="width:100%">
              <el-option label="BD" value="BD" />
              <el-option label="已赢" value="已赢" />
            </el-select>
          </div>
        </div>

        <div class="detail-field detail-field--full">
          <label>技能</label>
          <el-select
            v-model="detailForm.required_skills_arr"
            placeholder="请选择技能"
            filterable multiple collapse-tags collapse-tags-tooltip
            style="width:100%"
          >
            <el-option v-for="s in filterOptions.skills" :key="s" :label="s" :value="s" />
          </el-select>
        </div>

        <div class="detail-field detail-field--full">
          <label>详细要求</label>
          <el-input v-model="detailForm.description" type="textarea" :rows="3" />
        </div>

        <div class="detail-field detail-field--full">
          <label>工作内容</label>
          <el-input v-model="detailForm.job_content" type="textarea" :rows="3" />
        </div>

        <div class="detail-grid">
          <div class="detail-field">
            <label>工作地点</label>
            <el-select v-model="detailForm.location" placeholder="请选择" clearable style="width:100%">
              <el-option v-for="l in filterOptions.locations" :key="l" :label="l" :value="l" />
            </el-select>
          </div>
          <div class="detail-field">
            <label>匹配状态</label>
            <el-select v-model="detailForm.match_status" placeholder="请选择" clearable style="width:100%">
              <el-option label="待满足" value="待满足" />
              <el-option label="关闭-Core满足" value="关闭-Core满足" />
              <el-option label="关闭·部分满足" value="关闭·部分满足" />
              <el-option label="关闭·未满足" value="关闭·未满足" />
              <el-option label="关闭-需求取消" value="关闭-需求取消" />
              <el-option label="关闭-需求重开" value="关闭-需求重开" />
              <el-option label="已满足" value="已满足" />
            </el-select>
          </div>
        </div>

        <div class="detail-field detail-field--full">
          <label>推荐顾问名单</label>
          <el-select
            v-model="detailForm.consultant_ids"
            placeholder="请选择顾问"
            filterable multiple collapse-tags collapse-tags-tooltip
            style="width:100%"
          >
            <el-option v-for="e in employeeList" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="detailDialog.saving" @click="saveDetail">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增需求弹窗 -->
    <el-dialog
      v-model="createDialog.visible"
      title="新增项目需求"
      width="520px"
      :close-on-click-modal="false"
      :teleported="false"
      class="create-dialog"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-position="top"
        class="create-form"
      >
        <div class="form-grid">
          <el-form-item label="项目名称" prop="project_name">
            <el-input
              v-model="createForm.project_name"
              placeholder="请输入项目名称"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="Competency" prop="competency">
            <el-select
              v-model="createForm.competency"
              placeholder="请选择Competency"
              style="width: 100%"
            >
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
          </el-form-item>

          <el-form-item label="所需技能" prop="required_skills">
            <el-select
              v-model="createForm.required_skills"
              placeholder="请选择所需技能"
              filterable
              multiple
              collapse-tags
              collapse-tags-tooltip
              style="width: 100%"
            >
              <el-option v-for="s in filterOptions.skills" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>

          <el-form-item label="需求人数" prop="headcount">
            <el-input
              v-model.number="createForm.headcount"
              placeholder="请输入需求人数"
              type="number"
              :min="1"
            />
          </el-form-item>

          <el-form-item label="财年">
            <el-select v-model="createForm.fiscal_year" placeholder="请选择财年" clearable style="width: 100%">
              <el-option v-for="y in filterOptions.fiscal_years" :key="y" :label="y" :value="y" />
            </el-select>
          </el-form-item>

          <el-form-item label="所有机会">
            <el-select v-model="createForm.project_type" placeholder="请选择机会类型" clearable style="width: 100%">
              <el-option v-for="t in filterOptions.project_types" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>

          <el-form-item label="Location">
            <el-select v-model="createForm.location" placeholder="请选择地点" clearable style="width: 100%">
              <el-option v-for="l in filterOptions.locations" :key="l" :label="l" :value="l" />
            </el-select>
          </el-form-item>

          <el-form-item label="匹配状态">
            <el-select v-model="createForm.match_status" placeholder="请选择匹配状态" clearable style="width: 100%">
              <el-option label="待满足" value="待满足" />
              <el-option label="关闭-Core满足" value="关闭-Core满足" />
              <el-option label="关闭·部分满足" value="关闭·部分满足" />
              <el-option label="关闭·未满足" value="关闭·未满足" />
              <el-option label="关闭-需求取消" value="关闭-需求取消" />
              <el-option label="关闭-需求重开" value="关闭-需求重开" />
              <el-option label="已满足" value="已满足" />
            </el-select>
          </el-form-item>
        </div>

      </el-form>

      <template #footer>
        <el-button @click="createDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="createDialog.submitting" @click="submitCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { requirementApi } from '@/api/requirements'
import { employeeApi } from '@/api/employees'

// 详情弹窗
const detailDialog = reactive({ visible: false, saving: false })
const employeeList = ref([])
const epList = computed(() => employeeList.value.filter(e => e.grade === 'P'))
const emList = computed(() => employeeList.value.filter(e => e.grade === 'M' || e.grade === 'SM'))
const detailForm = reactive({
  id: null,
  project_name: '',
  competency: '',
  opportunity_type: '',
  requester: '',
  request_date: '',
  ep_id: null,
  em_id: null,
  project_start_date: '',
  project_end_date: '',
  headcount: null,
  required_skills_arr: [],
  description: '',
  job_content: '',
  location: '',
  match_status: '',
  consultant_ids: [],
})

async function openDetailDialog(row) {
  if (employeeList.value.length === 0) {
    const res = await employeeApi.list({ page: 1, page_size: 500 })
    employeeList.value = res.data.items || []
  }
  Object.assign(detailForm, {
    id: row.id,
    project_name: row.project_name || '',
    competency: row.competency || '',
    opportunity_type: row.opportunity_type || '',
    requester: row.requester || '',
    request_date: row.request_date || '',
    ep_id: row.ep_id || null,
    em_id: row.em_id || null,
    project_start_date: row.project_start_date || '',
    project_end_date: row.project_end_date || '',
    headcount: row.headcount || null,
    required_skills_arr: row.required_skills ? row.required_skills.split(',').map(s => s.trim()).filter(Boolean) : [],
    description: row.description || '',
    job_content: row.job_content || '',
    location: row.location || '',
    match_status: row.match_status || '',
    consultant_ids: row.consultants ? row.consultants.map(c => c.id) : [],
  })
  detailDialog.visible = true
}

async function saveDetail() {
  if (detailForm.project_start_date && detailForm.project_end_date) {
    if (detailForm.project_end_date < detailForm.project_start_date) {
      ElMessage.warning('项目结束时间不能早于项目开始时间')
      return
    }
  }
  detailDialog.saving = true
  try {
    await requirementApi.update(detailForm.id, {
      project_name: detailForm.project_name,
      competency: detailForm.competency || null,
      opportunity_type: detailForm.opportunity_type || null,
      ep_id: detailForm.ep_id || 0,
      em_id: detailForm.em_id || 0,
      project_start_date: detailForm.project_start_date || null,
      project_end_date: detailForm.project_end_date || null,
      headcount: detailForm.headcount ? Number(detailForm.headcount) : null,
      required_skills: detailForm.required_skills_arr.join(','),
      location: detailForm.location || null,
      match_status: detailForm.match_status || null,
      description: detailForm.description || null,
      job_content: detailForm.job_content || null,
      requester: detailForm.requester || null,
      request_date: detailForm.request_date || null,
      consultant_ids: detailForm.consultant_ids,
    })
    ElMessage.success('保存成功')
    detailDialog.visible = false
    loadData()
  } catch (e) {
    console.error(e)
    const msg = e?.response?.data?.detail || '保存失败'
    ElMessage.error(msg)
  } finally {
    detailDialog.saving = false
  }
}

// 新增弹窗
const createFormRef = ref(null)
const createDialog = reactive({ visible: false, submitting: false })
const createForm = reactive({
  project_name: '',
  competency: '',
  required_skills: [],
  headcount: null,
  fiscal_year: '',
  project_type: '',
  location: '',
  match_status: '',
  description: '',
})
const createRules = {
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  competency: [{ required: true, message: '请选择Competency', trigger: 'change' }],
  required_skills: [{ required: true, message: '请选择所需技能', trigger: 'change' }],
  headcount: [{ required: true, message: '请输入需求人数', trigger: 'blur' }],
}

function openCreateDialog() {
  Object.assign(createForm, {
    project_name: '', competency: '', required_skills: [],
    headcount: null, fiscal_year: '', project_type: '',
    location: '', match_status: '', description: '',
  })
  createDialog.visible = true
  createFormRef.value?.clearValidate()
}

async function submitCreate() {
  await createFormRef.value.validate()
  createDialog.submitting = true
  try {
    await requirementApi.create({
      project_name: createForm.project_name,
      competency: createForm.competency || null,
      opportunity_type: createForm.project_type || null,
      headcount: createForm.headcount,
      required_skills: createForm.required_skills.join(','),
      fiscal_year: createForm.fiscal_year || null,
      location: createForm.location || null,
      match_status: createForm.match_status || null,
      description: createForm.description || null,
    })
    ElMessage.success('新增成功')
    createDialog.visible = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error('新增失败')
  } finally {
    createDialog.submitting = false
  }
}

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

.filter-card :deep(.el-select__wrapper .el-tag),
.filter-card :deep(.el-select__tags-wrapper .el-tag),
.filter-card :deep(.el-select .el-tag) {
  background-color: rgba(0, 170, 204, 0.2) !important;
  border-color: rgba(0, 170, 204, 0.4) !important;
  color: #7ee8f8 !important;
  --el-tag-bg-color: rgba(0, 170, 204, 0.2) !important;
  --el-tag-border-color: rgba(0, 170, 204, 0.4) !important;
  --el-tag-text-color: #7ee8f8 !important;
}

.filter-card :deep(.el-select__wrapper .el-tag .el-tag__close),
.filter-card :deep(.el-select .el-tag .el-tag__close) {
  color: #7ee8f8 !important;
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

.project-name-cell {
  white-space: normal;
  word-break: break-word;
  line-height: 1.4;
  display: block;
  color: var(--accent-cyan);
  font-weight: 600;
  font-size: 13px;
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

/* 详情弹窗 */
:deep(.detail-dialog) {
  background-color: #0d1f35 !important;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

:deep(.detail-dialog .el-dialog__title) {
  color: var(--accent-cyan);
  font-weight: 600;
}

:deep(.detail-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-secondary);
}

.detail-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 20px;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-field--full {
  grid-column: 1 / -1;
}

.detail-field label {
  font-size: 12px;
  color: var(--text-secondary);
}

.detail-readonly {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-cyan);
  padding: 2px 0;
}

.detail-form :deep(.el-input__wrapper),
.detail-form :deep(.el-select__wrapper),
.detail-form :deep(.el-textarea__inner) {
  background-color: #0d1f35 !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
  border-radius: 8px !important;
}

.detail-form :deep(.el-input__inner),
.detail-form :deep(.el-input__inner::placeholder),
.detail-form :deep(.el-select__placeholder),
.detail-form :deep(.el-select__selected-item span),
.detail-form :deep(.el-textarea__inner),
.detail-form :deep(.el-textarea__inner::placeholder) {
  color: #ffffff !important;
}

.detail-form :deep(.el-select__wrapper .el-tag),
.detail-form :deep(.el-select .el-tag) {
  background-color: rgba(0, 170, 204, 0.2) !important;
  border-color: rgba(0, 170, 204, 0.4) !important;
  color: #7ee8f8 !important;
}

/* 新增需求弹窗 */
:deep(.create-dialog) {
  background-color: #0d1f35 !important;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

:deep(.create-dialog .el-dialog__title) {
  color: var(--accent-cyan);
  font-weight: 600;
}

:deep(.create-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-secondary);
}

.create-form :deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-size: 13px;
}

.create-form :deep(.el-input__wrapper),
.create-form :deep(.el-select__wrapper),
.create-form :deep(.el-textarea__inner) {
  background-color: #0d1f35 !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
  border-radius: 8px !important;
}

.create-form :deep(.el-input__inner),
.create-form :deep(.el-input__inner::placeholder),
.create-form :deep(.el-select__placeholder),
.create-form :deep(.el-select__selected-item span),
.create-form :deep(.el-textarea__inner),
.create-form :deep(.el-textarea__inner::placeholder) {
  color: #ffffff !important;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 20px;
}

.create-form :deep(.el-select__wrapper .el-tag),
.create-form :deep(.el-select__tags-wrapper .el-tag),
.create-form :deep(.el-select .el-tag) {
  background-color: rgba(0, 170, 204, 0.2) !important;
  border-color: rgba(0, 170, 204, 0.4) !important;
  color: #7ee8f8 !important;
  --el-tag-bg-color: rgba(0, 170, 204, 0.2) !important;
  --el-tag-border-color: rgba(0, 170, 204, 0.4) !important;
  --el-tag-text-color: #7ee8f8 !important;
}

.create-form :deep(.el-select__wrapper .el-tag .el-tag__close),
.create-form :deep(.el-select .el-tag .el-tag__close) {
  color: #7ee8f8 !important;
}
</style>

<style>
.el-picker__popper .el-date-picker {
  transform: scale(0.8);
  transform-origin: top left;
  border-radius: 12px !important;
  overflow: hidden;
}

.el-picker__popper,
.el-picker__popper.el-popper,
.el-picker__popper.el-popper.is-light {
  width: auto !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  background: transparent !important;
  padding: 0 !important;
}

.el-popper.is-light {
  background-color: #0d1f35 !important;
  border-color: rgba(0, 170, 204, 0.3) !important;
  color: #ffffff !important;
}

.el-popper.is-light .el-popper__arrow::before {
  background-color: #0d1f35 !important;
  border-color: rgba(0, 170, 204, 0.3) !important;
}

.el-popper.is-light .el-tag {
  background-color: rgba(0, 170, 204, 0.2) !important;
  border-color: rgba(0, 170, 204, 0.4) !important;
  color: #7ee8f8 !important;
}
</style>
