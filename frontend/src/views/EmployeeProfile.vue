<template>
  <div class="employee-profile" v-loading="pageLoading">
    <!-- Back button -->
    <div class="back-bar">
      <el-button link @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回员工列表
      </el-button>
    </div>

    <template v-if="employee">
      <!-- Info Card -->
      <el-card class="info-card">
        <div class="card-header">
          <!-- Avatar -->
          <div class="avatar-wrap" @click="triggerAvatarUpload">
            <el-avatar
              v-if="employee.avatar_url"
              :src="employee.avatar_url"
              :size="80"
              class="avatar"
            />
            <div v-else class="avatar-placeholder">
              {{ employee.name?.charAt(0) || '?' }}
            </div>
            <div class="avatar-overlay"><el-icon><Camera /></el-icon></div>
          </div>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onAvatarChange" />

          <!-- Name block -->
          <div class="name-block">
            <span class="name-cn">{{ employee.name }}</span>
            <span class="name-en">{{ employee.name_en || '' }}</span>
            <el-tag :type="statusTagType" size="small" class="status-tag">{{ statusLabel }}</el-tag>
          </div>

          <!-- Action buttons -->
          <div class="card-actions">
            <template v-if="!editing">
              <el-button type="primary" size="small" @click="startEdit">编辑</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button type="primary" size="small" :loading="saving" @click="saveEdit">保存</el-button>
            </template>
          </div>
        </div>

        <!-- Fields grid -->
        <div class="fields-grid">
          <div class="field-item">
            <span class="field-label">Competency</span>
            <span class="field-value">{{ employee.competency || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">GPN</span>
            <span class="field-value">{{ employee.gpn }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">职级</span>
            <span class="field-value">{{ employee.grade || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">Location</span>
            <span class="field-value" v-if="!editing">{{ employee.location || '—' }}</span>
            <el-input v-else v-model="editForm.location" size="small" class="edit-input" />
          </div>
          <div class="field-item">
            <span class="field-label">邮箱</span>
            <span class="field-value" v-if="!editing">{{ employee.email || '—' }}</span>
            <el-input v-else v-model="editForm.email" size="small" class="edit-input" />
          </div>
          <div class="field-item">
            <span class="field-label">电话</span>
            <span class="field-value" v-if="!editing">{{ employee.phone || '—' }}</span>
            <el-input v-else v-model="editForm.phone" size="small" class="edit-input" />
          </div>
          <div class="field-item">
            <span class="field-label">Counsellor</span>
            <span class="field-value">
              <template v-if="employee.counsellor_name">
                <el-popover placement="right" trigger="hover" :width="240" popper-class="counsellor-popover">
                  <template #reference>
                    <span class="counsellor-link">{{ employee.counsellor_name }}</span>
                  </template>
                  <div class="counsellor-card">
                    <div class="c-avatar">{{ counsellorInitials }}</div>
                    <div class="c-info">
                      <div class="c-name">{{ employee.counsellor_name }}</div>
                      <div class="c-name-en">{{ employee.counsellor_name_en || '' }}</div>
                      <div class="c-grade">{{ employee.counsellor_grade || '' }}</div>
                      <div class="c-email">{{ employee.counsellor_email || '' }}</div>
                    </div>
                  </div>
                </el-popover>
              </template>
              <template v-else>—</template>
            </span>
          </div>
          <div class="field-item">
            <span class="field-label">入职日期</span>
            <span class="field-value">{{ employee.join_date || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">当前项目</span>
            <span class="field-value">{{ employee.current_project?.name || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">YTD UT</span>
            <span class="field-value">{{ employee.ytd_ut != null ? employee.ytd_ut + '%' : '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">Effective UT</span>
            <span class="field-value">{{ employee.effective_ut != null ? employee.effective_ut + '%' : '—' }}</span>
          </div>
        </div>
      </el-card>

      <!-- Tabs Card -->
      <el-card class="tabs-card">
        <el-tabs v-model="activeTab" @tab-click="onTabClick">
          <!-- 技能评估 -->
          <el-tab-pane label="技能评估" name="skills">
            <div class="skills-tab">
              <!-- Radar chart -->
              <div class="radar-wrap">
                <template v-if="radarSkills.length > 0">
                  <v-chart :option="radarOption" autoresize class="radar-chart" />
                </template>
                <div v-else class="empty-radar">
                  <el-empty description="暂无技能数据" :image-size="80" />
                </div>
              </div>

              <!-- Skill list -->
              <div class="skill-list-wrap">
                <div class="skill-list">
                  <div v-for="(skill, idx) in skillList" :key="idx" class="skill-row">
                    <el-select
                      v-model="skill.skill_id"
                      placeholder="选择技能"
                      size="small"
                      class="skill-select"
                      filterable
                      @change="(val) => onSkillSelect(idx, val)"
                    >
                      <el-option
                        v-for="opt in availableSkillsFor(idx)"
                        :key="opt.id"
                        :label="opt.name"
                        :value="opt.id"
                      />
                    </el-select>
                    <el-select v-model="skill.level" size="small" class="level-select">
                      <el-option v-for="lv in levelOptions" :key="lv" :label="lv + '%'" :value="lv" />
                    </el-select>
                    <el-button type="danger" link size="small" @click="removeSkill(idx)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div class="skill-actions">
                  <el-button link size="small" @click="addSkill">
                    <el-icon><Plus /></el-icon> 添加技能
                  </el-button>
                  <el-button type="primary" size="small" :loading="skillSaving" @click="saveSkills">
                    保存技能
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 项目经历 -->
          <el-tab-pane label="项目经历" name="projects">
            <div v-if="projectsData === null" class="tab-loading">
              <el-skeleton :rows="4" animated />
            </div>
            <el-table v-else :data="projectsData" stripe size="small">
              <el-table-column prop="project_name" label="项目名称" min-width="160" />
              <el-table-column prop="project_code" label="项目代码" width="120" />
              <el-table-column prop="role" label="角色" width="120" />
              <el-table-column prop="team_name" label="团队" width="140" />
              <el-table-column prop="start_date" label="开始日期" width="110" />
              <el-table-column prop="end_date" label="结束日期" width="110" />
              <el-table-column label="是否当前" width="90" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.is_current" type="success" size="small">当前</el-tag>
                  <span v-else class="text-muted">—</span>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无项目经历" :image-size="60" />
              </template>
            </el-table>
          </el-tab-pane>

          <!-- 培训记录 -->
          <el-tab-pane label="培训记录" name="trainings">
            <div v-if="trainingsData === null" class="tab-loading">
              <el-skeleton :rows="4" animated />
            </div>
            <el-table v-else :data="trainingsData" stripe size="small">
              <el-table-column prop="training_name" label="培训名称" min-width="160" />
              <el-table-column prop="training_type" label="类型" width="110" />
              <el-table-column prop="hours" label="时长(小时)" width="100" align="right" />
              <el-table-column prop="start_date" label="开始日期" width="110" />
              <el-table-column prop="completed_date" label="完成日期" width="110" />
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="trainingStatusType(row.status)" size="small">
                    {{ trainingStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无培训记录" :image-size="60" />
              </template>
            </el-table>
          </el-tab-pane>

          <!-- 绩效考评 -->
          <el-tab-pane label="绩效考评" name="performances">
            <div v-if="performancesData === null" class="tab-loading">
              <el-skeleton :rows="4" animated />
            </div>
            <el-table v-else :data="performancesData" stripe size="small">
              <el-table-column prop="year" label="年份" width="80" align="center" />
              <el-table-column prop="quarter" label="季度" width="80" align="center">
                <template #default="{ row }">{{ row.quarter ? 'Q' + row.quarter : '年度' }}</template>
              </el-table-column>
              <el-table-column prop="rating" label="评级" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="ratingTagType(row.rating)" size="small">{{ row.rating || '—' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="voc_score" label="VoC 评分" width="100" align="right" />
              <el-table-column prop="comments" label="备注" min-width="200" show-overflow-tooltip />
              <template #empty>
                <el-empty description="暂无绩效记录" :image-size="60" />
              </template>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart } from 'echarts/charts'
import { RadarComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { employeeApi } from '@/api/employees'

use([CanvasRenderer, RadarChart, RadarComponent, TooltipComponent, LegendComponent])

const route = useRoute()
const employeeId = computed(() => Number(route.params.id))

// Page state
const pageLoading = ref(false)
const employee = ref(null)
const allSkillOptions = ref([]) // { id, name, category }

// Edit state
const editing = ref(false)
const saving = ref(false)
const editForm = reactive({ location: '', email: '', phone: '' })

// Avatar
const fileInput = ref(null)

// Skills tab
const skillList = ref([]) // { skill_id, skillName, level }
const skillSaving = ref(false)
const levelOptions = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

// Lazy-loaded tabs (null = not loaded yet)
const projectsData = ref(undefined) // undefined = tab never opened
const trainingsData = ref(undefined)
const performancesData = ref(undefined)

const activeTab = ref('skills')

// ─── Load page ───────────────────────────────────────────────
onMounted(async () => {
  pageLoading.value = true
  try {
    const [empRes, skillOptsRes] = await Promise.all([
      employeeApi.getById(employeeId.value),
      employeeApi.getSkillOptions(),
    ])
    employee.value = empRes.data
    allSkillOptions.value = skillOptsRes.data

    // Build editable skill list from loaded skills
    skillList.value = (employee.value.skills || []).map(s => ({
      skill_id: s.id,
      skillName: s.name,
      level: s.level,
    }))
  } catch (e) {
    ElMessage.error('加载员工信息失败')
  } finally {
    pageLoading.value = false
  }
})

// ─── Tab lazy loading ─────────────────────────────────────────
async function onTabClick() {
  const tab = activeTab.value
  if (tab === 'projects' && projectsData.value === undefined) {
    projectsData.value = null
    try {
      const res = await employeeApi.getProjects(employeeId.value)
      projectsData.value = res.data
    } catch {
      projectsData.value = []
      ElMessage.error('加载项目经历失败')
    }
  } else if (tab === 'trainings' && trainingsData.value === undefined) {
    trainingsData.value = null
    try {
      const res = await employeeApi.getTrainings(employeeId.value)
      trainingsData.value = res.data
    } catch {
      trainingsData.value = []
      ElMessage.error('加载培训记录失败')
    }
  } else if (tab === 'performances' && performancesData.value === undefined) {
    performancesData.value = null
    try {
      const res = await employeeApi.getPerformances(employeeId.value)
      performancesData.value = res.data
    } catch {
      performancesData.value = []
      ElMessage.error('加载绩效记录失败')
    }
  }
}

// ─── Edit info card ───────────────────────────────────────────
function startEdit() {
  editForm.location = employee.value.location || ''
  editForm.email = employee.value.email || ''
  editForm.phone = employee.value.phone || ''
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  saving.value = true
  try {
    const res = await employeeApi.update(employeeId.value, {
      location: editForm.location || null,
      email: editForm.email || null,
      phone: editForm.phone || null,
    })
    employee.value = res.data
    editing.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// ─── Avatar upload ────────────────────────────────────────────
function triggerAvatarUpload() {
  fileInput.value?.click()
}

async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  try {
    const res = await employeeApi.uploadAvatar(employeeId.value, file)
    employee.value.avatar_url = res.data.avatar_url
    ElMessage.success('头像上传成功')
  } catch {
    ElMessage.error('头像上传失败')
  } finally {
    e.target.value = ''
  }
}

// ─── Skills ───────────────────────────────────────────────────
function availableSkillsFor(idx) {
  const selectedIds = skillList.value
    .filter((_, i) => i !== idx)
    .map(s => s.skill_id)
    .filter(Boolean)
  return allSkillOptions.value.filter(o => !selectedIds.includes(o.id))
}

function onSkillSelect(idx, skillId) {
  const opt = allSkillOptions.value.find(o => o.id === skillId)
  if (opt) skillList.value[idx].skillName = opt.name
}

function addSkill() {
  skillList.value.push({ skill_id: null, skillName: '', level: 0 })
}

function removeSkill(idx) {
  skillList.value.splice(idx, 1)
}

async function saveSkills() {
  const valid = skillList.value.filter(s => s.skill_id != null)
  skillSaving.value = true
  try {
    await employeeApi.updateSkills(
      employeeId.value,
      valid.map(s => ({ skill_id: s.skill_id, level: s.level }))
    )
    // keep skillList in sync (remove rows with no skill selected)
    skillList.value = valid
    ElMessage.success('技能保存成功')
  } catch {
    ElMessage.error('技能保存失败')
  } finally {
    skillSaving.value = false
  }
}

// ─── Radar chart ──────────────────────────────────────────────
const radarSkills = computed(() => skillList.value.filter(s => s.skill_id).slice(0, 10))

const radarOption = computed(() => {
  const skills = radarSkills.value
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    radar: {
      indicator: skills.map(s => ({ name: s.skillName, max: 100 })),
      shape: 'polygon',
      splitNumber: 5,
      axisName: { color: '#a0b4c8', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      splitArea: { areaStyle: { color: ['rgba(0,0,0,0)', 'rgba(255,255,255,0.02)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: skills.map(s => s.level),
            name: '技能等级',
            areaStyle: { color: 'rgba(0,188,212,0.2)' },
            lineStyle: { color: '#00bcd4', width: 2 },
            itemStyle: { color: '#00bcd4' },
          },
        ],
      },
    ],
  }
})

// ─── Computed helpers ─────────────────────────────────────────
const statusLabel = computed(() => {
  const map = { '在项': '在项', bench: 'Bench', '休假': '休假' }
  return map[employee.value?.status] || employee.value?.status || '—'
})

const statusTagType = computed(() => {
  const map = { '在项': 'success', bench: 'info', '休假': 'warning' }
  return map[employee.value?.status] || 'info'
})

const counsellorInitials = computed(() => {
  const name = employee.value?.counsellor_name_en || employee.value?.counsellor_name || ''
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(w => w[0])
    .join('')
    .toUpperCase()
})

function trainingStatusLabel(status) {
  const map = { planned: '计划中', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status || '—'
}

function trainingStatusType(status) {
  const map = { planned: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}

function ratingTagType(rating) {
  const map = { EX: 'success', ME: 'primary', NI: 'danger' }
  return map[rating] || 'info'
}
</script>

<style scoped>
.employee-profile {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.back-bar {
  margin-bottom: -4px;
}

/* ── Info Card ── */
.info-card :deep(.el-card__body) {
  padding: 20px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.avatar-wrap {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #00bcd4;
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
  font-size: 20px;
}

.avatar-wrap:hover .avatar-overlay {
  opacity: 1;
}

.name-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-cn {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.name-en {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.status-tag {
  width: fit-content;
}

.card-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

/* ── Fields Grid ── */
.fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 32px;
}

.field-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 32px;
}

.field-label {
  width: 90px;
  flex-shrink: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.field-value {
  color: var(--el-text-color-primary);
  font-size: 13px;
  flex: 1;
}

.edit-input {
  flex: 1;
}

.counsellor-link {
  color: #00bcd4;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* ── Tabs Card ── */
.tabs-card :deep(.el-card__body) {
  padding: 0 16px 16px;
}

/* ── Skills Tab ── */
.skills-tab {
  display: flex;
  gap: 24px;
  min-height: 360px;
  padding-top: 8px;
}

.radar-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-chart {
  width: 100%;
  height: 320px;
}

.empty-radar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skill-list-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

.skill-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skill-select {
  flex: 1;
}

.level-select {
  width: 90px;
}

.skill-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 4px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* ── Tab loading ── */
.tab-loading {
  padding: 16px;
}

/* ── Misc ── */
.text-muted {
  color: var(--el-text-color-secondary);
}
</style>

<!-- Counsellor popover global style (teleported to body) -->
<style>
.counsellor-popover .counsellor-card {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.counsellor-popover .c-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #00bcd4;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.counsellor-popover .c-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.counsellor-popover .c-name {
  font-weight: 600;
  font-size: 14px;
}

.counsellor-popover .c-name-en,
.counsellor-popover .c-grade,
.counsellor-popover .c-email {
  font-size: 12px;
  color: #888;
}
</style>
