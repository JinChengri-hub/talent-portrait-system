<template>
  <div class="profile-page" v-loading="pageLoading">

    <!-- 顶部标题栏 -->
    <div class="page-header">
      <el-button link class="back-btn" @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <span class="page-title">员工画像</span>
    </div>

    <template v-if="employee">
      <!-- 信息卡片 -->
      <div class="info-card">

        <!-- 卡片顶部：头像 + 姓名 + 按钮 -->
        <div class="card-top">
          <div class="avatar-wrap" @click="triggerAvatarUpload" title="点击更换头像">
            <img v-if="employee.avatar_url" :src="employee.avatar_url" class="avatar-img" />
            <div v-else class="avatar-placeholder">{{ employee.name?.charAt(0) || '?' }}</div>
            <div class="avatar-overlay"><el-icon><Camera /></el-icon></div>
          </div>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onAvatarChange" />

          <div class="name-block">
            <div class="name-row">
              <span class="name-cn">{{ employee.name }}</span>
              <span v-if="employee.name_en" class="name-en">{{ employee.name_en }}</span>
              <span :class="['status-badge', statusClass]">{{ statusLabel }}</span>
            </div>
            <div class="sub-info">
              <span class="grade-badge" v-if="employee.grade">{{ employee.grade }}</span>
              <span class="sub-text" v-if="employee.competency">{{ employee.competency }}</span>
              <span class="sub-text" v-if="employee.gpn">GPN: {{ employee.gpn }}</span>
            </div>
          </div>

          <div class="card-actions">
            <template v-if="!editing">
              <el-button type="primary" size="small" @click="startEdit">编辑信息</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="cancelEdit">取消</el-button>
              <el-button type="primary" size="small" :loading="saving" @click="saveEdit">保存</el-button>
            </template>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="card-divider" />

        <!-- 字段网格 -->
        <div class="fields-grid">
          <div class="field-item">
            <span class="field-label">邮箱</span>
            <span v-if="!editing" class="field-value">{{ employee.email || '—' }}</span>
            <el-input v-else v-model="editForm.email" size="small" placeholder="输入邮箱" class="field-input" />
          </div>
          <div class="field-item">
            <span class="field-label">电话</span>
            <span v-if="!editing" class="field-value">{{ employee.phone || '—' }}</span>
            <el-input v-else v-model="editForm.phone" size="small" placeholder="输入电话" class="field-input" />
          </div>
          <div class="field-item">
            <span class="field-label">Location</span>
            <span v-if="!editing" class="field-value">{{ employee.location || '—' }}</span>
            <el-input v-else v-model="editForm.location" size="small" placeholder="输入城市" class="field-input" />
          </div>
          <div class="field-item">
            <span class="field-label">入职日期</span>
            <span class="field-value">{{ employee.join_date || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">Counsellor</span>
            <span class="field-value">
              <template v-if="employee.counsellor_name">
                <el-popover placement="right" trigger="hover" :width="240" popper-class="counsellor-pop">
                  <template #reference>
                    <span class="link-text">{{ employee.counsellor_name }}</span>
                  </template>
                  <div class="c-card">
                    <div class="c-avatar">{{ counsellorInitials }}</div>
                    <div class="c-info">
                      <div class="c-name">{{ employee.counsellor_name }}</div>
                      <div v-if="employee.counsellor_name_en" class="c-sub">{{ employee.counsellor_name_en }}</div>
                      <div v-if="employee.counsellor_grade" class="c-sub">{{ employee.counsellor_grade }}</div>
                      <div v-if="employee.counsellor_email" class="c-sub">{{ employee.counsellor_email }}</div>
                    </div>
                  </div>
                </el-popover>
              </template>
              <template v-else>—</template>
            </span>
          </div>
          <div class="field-item">
            <span class="field-label">当前项目</span>
            <span class="field-value link-text">{{ employee.current_project?.name || '—' }}</span>
          </div>
          <div class="field-item">
            <span class="field-label">YTD UT</span>
            <span class="field-value accent">
              {{ employee.ytd_ut != null ? employee.ytd_ut + '%' : '—' }}
            </span>
          </div>
          <div class="field-item">
            <span class="field-label">Effective UT</span>
            <span class="field-value accent">
              {{ employee.effective_ut != null ? employee.effective_ut + '%' : '—' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tab 面板 -->
      <div class="tab-card">
        <el-tabs v-model="activeTab" class="profile-tabs" @tab-click="onTabClick">

          <!-- 技能评估 -->
          <el-tab-pane label="技能评估" name="skills">
            <div class="skills-tab">
              <!-- 左：雷达图 -->
              <div class="radar-panel">
                <v-chart v-if="radarSkills.length > 0" :option="radarOption" autoresize class="radar-chart" />
                <el-empty v-else description="暂无技能数据，请在右侧添加" :image-size="80" />
              </div>

              <!-- 右：技能列表 -->
              <div class="skill-panel">
                <div class="skill-panel-header">
                  <span class="panel-title">技能评估列表</span>
                  <el-button type="primary" size="small" :loading="skillSaving" @click="saveSkills">保存技能</el-button>
                </div>
                <div class="skill-list">
                  <div v-if="skillList.length === 0" class="skill-empty">暂无技能，点击下方按钮添加</div>
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
                <div class="skill-add-row">
                  <el-button link size="small" class="add-skill-btn" @click="addSkill">
                    <el-icon><Plus /></el-icon> 添加技能
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 项目经历 -->
          <el-tab-pane label="项目经历" name="projects">
            <div v-if="projectsData === null" class="tab-skeleton">
              <el-skeleton :rows="5" animated />
            </div>
            <el-table v-else :data="projectsData || []" class="tab-table">
              <el-table-column prop="project_name" label="项目名称" min-width="180" />
              <el-table-column prop="project_code" label="项目代码" width="130" />
              <el-table-column prop="role" label="角色" width="120" />
              <el-table-column prop="team_name" label="团队" width="140" />
              <el-table-column prop="start_date" label="开始日期" width="110" />
              <el-table-column prop="end_date" label="结束日期" width="110" />
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <span v-if="row.is_current" class="status-badge status-on">当前</span>
                  <span v-else class="muted-text">—</span>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无项目经历" :image-size="60" />
              </template>
            </el-table>
          </el-tab-pane>

          <!-- 培训记录 -->
          <el-tab-pane label="培训记录" name="trainings">
            <div v-if="trainingsData === null" class="tab-skeleton">
              <el-skeleton :rows="5" animated />
            </div>
            <el-table v-else :data="trainingsData || []" class="tab-table">
              <el-table-column prop="training_name" label="培训名称" min-width="180" />
              <el-table-column prop="training_type" label="类型" width="120" />
              <el-table-column prop="hours" label="时长(小时)" width="100" align="right" />
              <el-table-column prop="start_date" label="开始日期" width="110" />
              <el-table-column prop="completed_date" label="完成日期" width="110" />
              <el-table-column label="状态" width="90" align="center">
                <template #default="{ row }">
                  <span :class="['training-badge', 'training-' + row.status]">
                    {{ trainingStatusLabel(row.status) }}
                  </span>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无培训记录" :image-size="60" />
              </template>
            </el-table>
          </el-tab-pane>

          <!-- 绩效考评 -->
          <el-tab-pane label="绩效考评" name="performances">
            <div v-if="performancesData === null" class="tab-skeleton">
              <el-skeleton :rows="5" animated />
            </div>
            <el-table v-else :data="performancesData || []" class="tab-table">
              <el-table-column prop="year" label="年份" width="80" align="center" />
              <el-table-column label="季度" width="80" align="center">
                <template #default="{ row }">{{ row.quarter ? 'Q' + row.quarter : '年度' }}</template>
              </el-table-column>
              <el-table-column label="评级" width="80" align="center">
                <template #default="{ row }">
                  <span :class="['rating-badge', 'rating-' + row.rating]">{{ row.rating || '—' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="voc_score" label="VoC 评分" width="100" align="right" />
              <el-table-column prop="comments" label="备注" min-width="220" show-overflow-tooltip />
              <template #empty>
                <el-empty description="暂无绩效记录" :image-size="60" />
              </template>
            </el-table>
          </el-tab-pane>

        </el-tabs>
      </div>
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

const pageLoading = ref(false)
const employee = ref(null)
const allSkillOptions = ref([])

const editing = ref(false)
const saving = ref(false)
const editForm = reactive({ location: '', email: '', phone: '' })

const fileInput = ref(null)

const skillList = ref([])
const skillSaving = ref(false)
const levelOptions = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

const projectsData = ref(undefined)
const trainingsData = ref(undefined)
const performancesData = ref(undefined)
const activeTab = ref('skills')

onMounted(async () => {
  pageLoading.value = true
  try {
    const [empRes, skillOptsRes] = await Promise.all([
      employeeApi.getById(employeeId.value),
      employeeApi.getSkillOptions(),
    ])
    employee.value = empRes.data
    allSkillOptions.value = skillOptsRes.data
    skillList.value = (employee.value.skills || []).map(s => ({
      skill_id: s.id,
      skillName: s.name,
      level: s.level,
    }))
  } catch {
    ElMessage.error('加载员工信息失败')
  } finally {
    pageLoading.value = false
  }
})

async function onTabClick() {
  const tab = activeTab.value
  if (tab === 'projects' && projectsData.value === undefined) {
    projectsData.value = null
    try { projectsData.value = (await employeeApi.getProjects(employeeId.value)).data }
    catch { projectsData.value = []; ElMessage.error('加载项目经历失败') }
  } else if (tab === 'trainings' && trainingsData.value === undefined) {
    trainingsData.value = null
    try { trainingsData.value = (await employeeApi.getTrainings(employeeId.value)).data }
    catch { trainingsData.value = []; ElMessage.error('加载培训记录失败') }
  } else if (tab === 'performances' && performancesData.value === undefined) {
    performancesData.value = null
    try { performancesData.value = (await employeeApi.getPerformances(employeeId.value)).data }
    catch { performancesData.value = []; ElMessage.error('加载绩效记录失败') }
  }
}

function startEdit() {
  editForm.location = employee.value.location || ''
  editForm.email = employee.value.email || ''
  editForm.phone = employee.value.phone || ''
  editing.value = true
}
function cancelEdit() { editing.value = false }
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
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

function triggerAvatarUpload() { fileInput.value?.click() }
async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) { ElMessage.error('图片大小不能超过 2MB'); return }
  try {
    const res = await employeeApi.uploadAvatar(employeeId.value, file)
    employee.value.avatar_url = res.data.avatar_url
    ElMessage.success('头像上传成功')
  } catch { ElMessage.error('头像上传失败') }
  finally { e.target.value = '' }
}

function availableSkillsFor(idx) {
  const selectedIds = skillList.value.filter((_, i) => i !== idx).map(s => s.skill_id).filter(Boolean)
  return allSkillOptions.value.filter(o => !selectedIds.includes(o.id))
}
function onSkillSelect(idx, skillId) {
  const opt = allSkillOptions.value.find(o => o.id === skillId)
  if (opt) skillList.value[idx].skillName = opt.name
}
function addSkill() { skillList.value.push({ skill_id: null, skillName: '', level: 0 }) }
function removeSkill(idx) { skillList.value.splice(idx, 1) }
async function saveSkills() {
  const valid = skillList.value.filter(s => s.skill_id != null)
  skillSaving.value = true
  try {
    await employeeApi.updateSkills(employeeId.value, valid.map(s => ({ skill_id: s.skill_id, level: s.level })))
    skillList.value = valid
    ElMessage.success('技能保存成功')
  } catch { ElMessage.error('技能保存失败') }
  finally { skillSaving.value = false }
}

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
      axisName: { color: '#8ab4d4', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(26,58,92,0.8)' } },
      splitArea: { areaStyle: { color: ['rgba(0,0,0,0)', 'rgba(0,212,255,0.03)'] } },
      axisLine: { lineStyle: { color: '#1a3a5c' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: skills.map(s => s.level),
        name: '技能等级',
        areaStyle: { color: 'rgba(0,212,255,0.15)' },
        lineStyle: { color: '#00d4ff', width: 2 },
        itemStyle: { color: '#00d4ff' },
      }],
    }],
  }
})

const statusLabel = computed(() => {
  const map = { '在项': '在项', bench: 'Bench', '休假': '休假' }
  return map[employee.value?.status] || employee.value?.status || '—'
})
const statusClass = computed(() => {
  const map = { '在项': 'status-on', bench: 'status-bench', '休假': 'status-leave' }
  return map[employee.value?.status] || 'status-bench'
})
const counsellorInitials = computed(() => {
  const name = employee.value?.counsellor_name_en || employee.value?.counsellor_name || ''
  return name.split(' ').filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase()
})
function trainingStatusLabel(s) {
  return { planned: '计划中', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }[s] || s || '—'
}
</script>

<style scoped>
/* ── 页面容器 ── */
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 2px;
  min-height: 100%;
}

/* ── 顶部标题 ── */
.page-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.back-btn {
  color: var(--text-secondary) !important;
  font-size: 13px;
  padding: 0;
}
.back-btn:hover { color: var(--accent-cyan) !important; }

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--accent-cyan);
  letter-spacing: 0.5px;
}

/* ── 公共卡片 ── */
.info-card,
.tab-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

/* ── 信息卡片顶部 ── */
.card-top {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #0d2540 0%, var(--bg-card) 100%);
}

.card-divider {
  height: 1px;
  background-color: var(--border-color);
}

/* ── 头像 ── */
.avatar-wrap {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
  width: 72px;
  height: 72px;
}

.avatar-img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-color);
}

.avatar-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #004d6b, #00d4ff33);
  border: 2px solid var(--accent-cyan-dim);
  color: var(--accent-cyan);
  font-size: 26px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
  font-size: 18px;
}
.avatar-wrap:hover .avatar-overlay { opacity: 1; }

/* ── 姓名区块 ── */
.name-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.name-cn {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.name-en {
  font-size: 14px;
  color: var(--text-secondary);
}

.sub-info {
  display: flex;
  align-items: center;
  gap: 10px;
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

.sub-text {
  font-size: 13px;
  color: var(--text-secondary);
}

/* ── 状态徽章 ── */
.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.status-on {
  background: rgba(0, 230, 118, 0.12);
  border: 1px solid rgba(0, 230, 118, 0.4);
  color: var(--accent-green);
}
.status-bench {
  background: rgba(120, 144, 156, 0.12);
  border: 1px solid rgba(120, 144, 156, 0.4);
  color: #90a4ae;
}
.status-leave {
  background: rgba(255, 152, 0, 0.12);
  border: 1px solid rgba(255, 152, 0, 0.4);
  color: var(--accent-orange);
}

/* ── 操作按钮 ── */
.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

/* ── 字段网格 ── */
.fields-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding: 0;
}

.field-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-right: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  min-height: 48px;
  transition: background-color 0.15s;
}

.field-item:nth-child(4n) {
  border-right: none;
}

.field-item:nth-last-child(-n+4) {
  border-bottom: none;
}

.field-item:hover {
  background-color: var(--bg-hover);
}

.field-label {
  width: 76px;
  flex-shrink: 0;
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.3px;
}

.field-value {
  font-size: 13px;
  color: var(--text-primary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.field-value.accent {
  color: var(--accent-cyan);
  font-weight: 500;
}

.field-input {
  flex: 1;
}

/* 编辑模式输入框适配暗色 */
:deep(.field-input .el-input__wrapper) {
  background-color: rgba(10, 22, 40, 0.8) !important;
  border-color: var(--accent-cyan-dim) !important;
  box-shadow: 0 0 0 1px var(--accent-cyan-dim) inset !important;
  border-radius: 4px !important;
}

.link-text {
  color: var(--accent-cyan);
  cursor: pointer;
}
.link-text:hover { text-decoration: underline; }

/* ── Tab 卡片 ── */
.tab-card {
  flex: 1;
}

/* ── el-tabs 暗色主题覆盖 ── */
:deep(.profile-tabs .el-tabs__header) {
  background-color: #0d2540;
  margin: 0;
  border-bottom: 1px solid var(--border-color);
  padding: 0 16px;
}

:deep(.profile-tabs .el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.profile-tabs .el-tabs__item) {
  color: var(--text-secondary);
  font-size: 14px;
  height: 44px;
  line-height: 44px;
  padding: 0 20px;
  transition: color 0.2s;
}

:deep(.profile-tabs .el-tabs__item:hover) {
  color: var(--text-primary);
}

:deep(.profile-tabs .el-tabs__item.is-active) {
  color: var(--accent-cyan);
  font-weight: 600;
}

:deep(.profile-tabs .el-tabs__active-bar) {
  background-color: var(--accent-cyan);
  height: 2px;
}

:deep(.profile-tabs .el-tabs__content) {
  padding: 0;
}

/* ── 表格样式 ── */
.tab-table {
  width: 100%;
}

:deep(.tab-table .el-table__row:hover > td) {
  background-color: var(--bg-hover) !important;
}

/* ── 技能 Tab ── */
.skills-tab {
  display: flex;
  min-height: 380px;
}

.radar-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--border-color);
  padding: 20px;
}

.radar-chart {
  width: 100%;
  height: 340px;
}

.skill-panel {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.skill-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  background-color: #0d2540;
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.skill-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skill-empty {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 32px 0;
}

.skill-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  border-bottom: 1px solid var(--border-color);
}

.skill-select { flex: 1; }
.level-select { width: 80px; }

.skill-add-row {
  padding: 10px 16px;
  border-top: 1px solid var(--border-color);
}

.add-skill-btn {
  color: var(--accent-cyan) !important;
  font-size: 13px;
}

/* ── Tab 骨架屏 ── */
.tab-skeleton {
  padding: 20px 24px;
}

/* ── 徽章 ── */
.muted-text {
  color: var(--text-muted);
}

.training-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
}
.training-planned    { background: rgba(120,144,156,0.15); color: #90a4ae; }
.training-in_progress { background: rgba(255,152,0,0.15); color: var(--accent-orange); }
.training-completed  { background: rgba(0,230,118,0.12); color: var(--accent-green); }
.training-cancelled  { background: rgba(239,83,80,0.12); color: var(--accent-red); }

.rating-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 600;
}
.rating-EX { background: rgba(0,230,118,0.12); color: var(--accent-green); border: 1px solid rgba(0,230,118,0.3); }
.rating-ME { background: rgba(0,212,255,0.1);  color: var(--accent-cyan);  border: 1px solid rgba(0,212,255,0.3); }
.rating-NI { background: rgba(239,83,80,0.12); color: var(--accent-red);   border: 1px solid rgba(239,83,80,0.3); }
</style>

<!-- Counsellor 弹出卡片（teleport 到 body，需用全局 style） -->
<style>
.counsellor-pop {
  background-color: #0f2744 !important;
  border: 1px solid #1a3a5c !important;
  border-radius: 8px !important;
}

.counsellor-pop .el-popper__arrow::before {
  background-color: #0f2744 !important;
  border-color: #1a3a5c !important;
}

.c-card {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 4px 0;
}

.c-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #004d6b, #00d4ff33);
  border: 1px solid #00aacc;
  color: #00d4ff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.c-info { display: flex; flex-direction: column; gap: 3px; }

.c-name {
  font-size: 14px;
  font-weight: 600;
  color: #e0f0ff;
}

.c-sub {
  font-size: 12px;
  color: #8ab4d4;
}
</style>
