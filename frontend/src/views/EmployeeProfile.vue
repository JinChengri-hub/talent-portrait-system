<template>
  <div class="profile-page" v-loading="pageLoading">

    <!-- 顶部标题栏 -->
    <div class="page-header">
      <span class="page-title">员工画像</span>
      <el-button link class="back-btn" @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回员工列表
      </el-button>
    </div>

    <template v-if="employee">
      <!-- 信息卡片 -->
      <div class="info-card">
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" style="display:none" @change="onAvatarChange" />

        <!-- 左：头像区 -->
        <div class="avatar-section">
          <div class="avatar-wrap" @click="triggerAvatarUpload" title="点击更换头像">
            <img v-if="employee.avatar_url" :src="employee.avatar_url" class="avatar-img" />
            <div v-else class="avatar-placeholder">{{ employee.name?.charAt(0) || '?' }}</div>
            <div class="avatar-overlay"><el-icon><Camera /></el-icon></div>
          </div>
          <span :class="['status-badge', statusClass]">{{ statusLabel }}</span>
        </div>

        <!-- 右：字段区 -->
        <div class="fields-section">

          <!-- 右上：姓名 + 编辑按钮 -->
          <div class="fields-header">
            <div class="name-row">
              <span class="name-cn">{{ employee.name }}</span>
              <span v-if="employee.name_en" class="name-en">{{ employee.name_en }}</span>
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

          <!-- 两列字段网格 -->
          <div class="fields-grid">

            <!-- 左列 -->
            <div class="fields-col">
              <div class="field-row">
                <el-icon class="field-icon"><OfficeBuilding /></el-icon>
                <span class="field-label">Competency：</span>
                <span class="field-value">{{ employee.competency || '—' }}</span>
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><Medal /></el-icon>
                <span class="field-label">职级：</span>
                <span class="field-value">{{ employee.grade || '—' }}</span>
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><Phone /></el-icon>
                <span class="field-label">电话：</span>
                <span v-if="!editing" class="field-value">{{ employee.phone || '—' }}</span>
                <el-input v-else v-model="editForm.phone" size="small" placeholder="输入电话" class="field-input" />
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><Folder /></el-icon>
                <span class="field-label">当前项目：</span>
                <span class="field-value">{{ employee.current_project?.name || '—' }}</span>
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><TrendCharts /></el-icon>
                <span class="field-label">YTD UT：</span>
                <span class="field-value">{{ employee.ytd_ut != null ? employee.ytd_ut + '%' : '—' }}</span>
                <span class="ut-divider">|</span>
                <el-icon class="field-icon"><DataAnalysis /></el-icon>
                <span class="field-label">Effective UT：</span>
                <span class="field-value">{{ employee.effective_ut != null ? employee.effective_ut + '%' : '—' }}</span>
              </div>
            </div>

            <!-- 右列 -->
            <div class="fields-col">
              <div class="field-row">
                <el-icon class="field-icon"><Postcard /></el-icon>
                <span class="field-label">员工ID：</span>
                <span class="field-value">{{ employee.gpn }}</span>
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><UserFilled /></el-icon>
                <span class="field-label">Counsellor：</span>
                <template v-if="employee.counsellor_name">
                  <el-popover placement="right" trigger="hover" :width="240" popper-class="counsellor-pop">
                    <template #reference>
                      <span class="field-value link-text">{{ employee.counsellor_name }}</span>
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
                <span v-else class="field-value">—</span>
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><Message /></el-icon>
                <span class="field-label">邮箱：</span>
                <span v-if="!editing" class="field-value">{{ employee.email || '—' }}</span>
                <el-input v-else v-model="editForm.email" size="small" placeholder="输入邮箱" class="field-input" />
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><Calendar /></el-icon>
                <span class="field-label">入职日期：</span>
                <span class="field-value">{{ employee.join_date || '—' }}</span>
              </div>
              <div class="field-row">
                <el-icon class="field-icon"><Location /></el-icon>
                <span class="field-label">Location：</span>
                <span v-if="!editing" class="field-value">{{ employee.location || '—' }}</span>
                <el-input v-else v-model="editForm.location" size="small" placeholder="输入城市" class="field-input" />
              </div>
            </div>

          </div>

        </div>

      </div>

      <!-- Tab 面板 -->
      <div class="tab-card">
        <el-tabs v-model="activeTab" class="profile-tabs" @tab-click="onTabClick">

          <!-- 技能评估 -->
          <el-tab-pane name="skills">
            <template #label>
              <span class="tab-label"><el-icon><Aim /></el-icon>技能评估</span>
            </template>
            <div class="skills-tab">

              <!-- 左：雷达图卡片 -->
              <div class="radar-panel">
                <v-chart v-if="radarSkills.length > 0" :option="radarOption" autoresize class="radar-chart" />
                <el-empty v-else description="暂无技能数据" :image-size="80" />
              </div>

              <!-- 右：技能详情展示 -->
              <div class="skill-panel">
                <div class="skill-panel-header">
                  <span class="panel-title">技能详情</span>
                  <el-button v-if="!skillEditing" type="primary" size="small" @click="skillEditing = true">编辑技能</el-button>
                </div>

                <!-- 统一列表：展示 + 编辑 -->
                <div class="skill-detail-list">
                  <div v-if="skillList.length === 0" class="skill-empty">
                    {{ skillEditing ? '暂无技能，点击下方按钮添加' : '暂无技能数据' }}
                  </div>
                  <div v-for="(skill, idx) in skillList" :key="idx" class="skill-detail-item">
                    <div class="skill-detail-top">
                      <span v-if="!skillEditing || !skill.isNew" class="skill-detail-name">{{ skill.skillName || '未选择' }}</span>
                      <el-select
                        v-else
                        v-model="skill.skill_id"
                        placeholder="选择技能"
                        size="small"
                        class="skill-edit-select"
                        popper-class="skill-select-dropdown"
                        placement="bottom-end"
                        filterable
                        @change="(val) => onSkillSelect(idx, val)"
                      >
                        <el-option v-for="opt in availableSkillsFor(idx)" :key="opt.id" :label="opt.name" :value="opt.id" />
                      </el-select>
                      <div class="skill-detail-right">
                        <span class="skill-detail-pct">{{ skill.level }}%</span>
                        <el-button v-if="skillEditing" type="danger" link size="small" class="skill-del-btn" @click="removeSkill(idx)">
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                    </div>
                    <div class="skill-segments">
                      <div
                        v-for="i in 10"
                        :key="i"
                        class="skill-segment"
                        :class="{ active: i <= Math.round(skill.level / 10), clickable: skillEditing }"
                        @click="skillEditing && (skill.level = i * 10)"
                      ></div>
                    </div>
                  </div>
                </div>

                <!-- 编辑底部操作栏 -->
                <div v-if="skillEditing" class="skill-edit-footer">
                  <el-button link size="small" class="add-skill-btn" @click="addSkill">
                    <el-icon><Plus /></el-icon> 添加技能
                  </el-button>
                  <el-button type="primary" size="small" :loading="skillSaving" @click="saveSkills">保存并关闭</el-button>
                </div>

              </div>
            </div>
          </el-tab-pane>

          <!-- 项目经历 -->
          <el-tab-pane name="projects">
            <template #label>
              <span class="tab-label"><el-icon><Briefcase /></el-icon>项目经历</span>
            </template>
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
          <el-tab-pane name="trainings">
            <template #label>
              <span class="tab-label"><el-icon><Reading /></el-icon>培训记录</span>
            </template>
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
          <el-tab-pane name="performances">
            <template #label>
              <span class="tab-label"><el-icon><TrendCharts /></el-icon>绩效考评</span>
            </template>
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
const skillEditing = ref(false)

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
      isNew: false,
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
function addSkill() { skillList.value.push({ skill_id: null, skillName: '', level: 0, isNew: true }) }
function removeSkill(idx) { skillList.value.splice(idx, 1) }
async function saveSkills() {
  const valid = skillList.value.filter(s => s.skill_id != null)
  skillSaving.value = true
  try {
    await employeeApi.updateSkills(employeeId.value, valid.map(s => ({ skill_id: s.skill_id, level: s.level })))
    skillList.value = valid.map(s => ({ ...s, isNew: false }))
    skillEditing.value = false
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
  justify-content: space-between;
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
  background-color: #0d2540;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

/* ═══════════════════════════════
   信息卡片：左右分区布局
   ═══════════════════════════════ */
.info-card {
  display: flex;
  align-items: stretch;
  padding: 16px 20px;
  gap: 50px;
  background: linear-gradient(135deg, #0a1f38 0%, var(--bg-card) 60%);
}

/* ── 左：头像区 ── */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  width: 120px;
  padding-top: 10px;
}

.avatar-wrap {
  position: relative;
  cursor: pointer;
  width: 108px;
  height: 108px;
  border-radius: 50%;
  /* 发光边框效果 */
  box-shadow:
    0 0 0 3px var(--accent-cyan),
    0 0 16px rgba(0, 212, 255, 0.45),
    0 0 32px rgba(0, 212, 255, 0.15);
}

.avatar-img {
  width: 108px;
  height: 108px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  width: 108px;
  height: 108px;
  border-radius: 50%;
  background: linear-gradient(135deg, #003d5c 0%, #005f80 100%);
  color: var(--accent-cyan);
  font-size: 36px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
  font-size: 20px;
}
.avatar-wrap:hover .avatar-overlay { opacity: 1; }

/* ── 状态徽章（头像下方） ── */
.status-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-align: center;
  width: 100%;
}
.status-on {
  background: rgba(0, 230, 118, 0.2);
  border: 1px solid rgba(0, 230, 118, 0.5);
  color: var(--accent-green);
}
.status-bench {
  background: rgba(120, 144, 156, 0.2);
  border: 1px solid rgba(120, 144, 156, 0.4);
  color: #90a4ae;
}
.status-leave {
  background: rgba(255, 152, 0, 0.18);
  border: 1px solid rgba(255, 152, 0, 0.45);
  color: var(--accent-orange);
}

/* ── 右：字段区 ── */
.fields-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

/* 姓名行 + 编辑按钮 */
.fields-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 6px;
}

.name-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.name-cn {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.name-en {
  font-size: 13px;
  color: var(--text-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

/* ── 两列字段网格 ── */
.fields-grid {
  display: flex;
  gap: 0;
  flex: 1;
}

.fields-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.fields-col:first-child {
  padding-right: 16px;
  margin-right: 16px;
}

.ut-divider {
  color: var(--border-color);
  margin: 0 4px;
  font-size: 14px;
}

/* 单行字段 */
.field-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
}
.field-row:last-child { border-bottom: none; }


.field-icon {
  font-size: 14px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.field-label {
  flex-shrink: 0;
  font-size: 15px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.field-value {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-value.accent,
.accent {
  color: var(--accent-cyan);
  font-weight: 600;
}

.field-input {
  flex: 1;
  min-width: 0;
}

:deep(.field-input .el-input__wrapper) {
  background-color: rgba(10, 22, 40, 0.8) !important;
  border-color: var(--accent-cyan-dim) !important;
  box-shadow: 0 0 0 1px var(--accent-cyan-dim) inset !important;
  border-radius: 4px !important;
  padding: 0 8px !important;
}

/* 职级徽章 */
.grade-badge {
  display: inline-block;
  padding: 1px 10px;
  background-color: rgba(0, 170, 204, 0.18);
  border: 1px solid var(--accent-cyan-dim);
  border-radius: 4px;
  color: var(--accent-cyan);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
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

/* ── tab 标签图标 ── */
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
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

:deep(.tab-table .el-table__row > td) {
  background-color: transparent !important;
}

:deep(.tab-table .el-table__row:hover > td) {
  background-color: var(--bg-hover) !important;
}

/* ── 技能 Tab ── */
.skills-tab {
  display: flex;
  gap: 20px;
  padding: 16px;
  align-items: flex-start;
}

.radar-panel {
  width: 520px;
  height: 400px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  min-width: 0;
}

.radar-chart {
  width: 100%;
  height: 340px;
}

.skill-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
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

.skill-empty {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 32px 0;
}

.skill-edit-select {
  width: 150px;
  flex-shrink: 0;
}

:deep(.skill-edit-select .el-select__wrapper) {
  background-color: transparent !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
  border-radius: 6px !important;
}

:deep(.skill-edit-select .el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-cyan-dim) inset !important;
}

:deep(.skill-edit-select .el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px var(--accent-cyan) inset !important;
}

:deep(.skill-edit-select .el-select__placeholder),
:deep(.skill-edit-select .el-select__selected-item span) {
  color: var(--text-primary) !important;
  font-size: 13px;
}

.skill-del-btn {
  flex-shrink: 0;
  color: var(--accent-red) !important;
}

.skill-edit-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px 14px;
  border-top: 1px solid var(--border-color);
}

.add-skill-btn {
  color: var(--accent-cyan) !important;
  font-size: 13px;
}

/* 技能详情展示（进度条模式） */
.skill-detail-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.skill-detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skill-detail-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skill-detail-name {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-detail-right {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.skill-detail-pct {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-cyan);
}

.skill-segments {
  display: flex;
  gap: 4px;
}

.skill-segment {
  flex: 1;
  height: 8px;
  border-radius: 2px;
  background-color: rgba(26, 58, 92, 0.9);
  transition: background-color 0.4s ease;
}

.skill-segment.active {
  background: linear-gradient(90deg, var(--accent-cyan-dim), var(--accent-cyan));
}

.skill-segment.clickable {
  cursor: pointer;
}

.skill-segment.clickable:hover {
  background-color: rgba(0, 170, 204, 0.5);
}

.skill-segment.clickable.active:hover {
  background: linear-gradient(90deg, var(--accent-cyan-dim), var(--accent-cyan));
  filter: brightness(1.3);
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
