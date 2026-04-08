```vue
<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans p-4 md:p-8">
    <div class="max-w-6xl mx-auto space-y-6">
      
      <!-- Header -->
      <header class="flex items-center justify-between pb-4 border-b border-slate-200">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-slate-900 flex items-center gap-3">
            <span class="p-2 bg-emerald-600 text-white rounded-lg shadow-sm">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>
            </span>
            Excel AI 数据工作台 
            <span class="text-xs font-normal px-2 py-1 bg-emerald-100 text-emerald-800 rounded-full ml-2 hidden md:inline-flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-600 mr-1"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
              纯本地处理
            </span>
          </h1>
          <p class="text-slate-500 mt-2 text-sm">无需上传服务器，保护核心商业数据。使用 AI 生成逻辑，本地瞬间完成数据清洗、处理或模拟生成。</p>
        </div>
        <button 
          v-if="history.length > 0"
          @click="handleDownload"
          class="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg font-medium transition-colors shadow-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          保存全部工作表
        </button>
      </header>

      <div v-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm">
        <p class="text-red-700 text-sm">{{ error }}</p>
      </div>

      <!-- Local Import -->
      <div v-if="history.length === 0" class="mt-12 flex flex-col items-center">
        <div 
          :class="[
            'w-full max-w-2xl border-2 border-dashed rounded-2xl p-16 flex flex-col items-center justify-center text-center transition-all',
            isDragging ? 'border-emerald-500 bg-emerald-50 scale-[1.02]' : 'border-slate-300 bg-white hover:border-emerald-400 hover:bg-slate-50',
            !xlsxLoaded ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer shadow-sm hover:shadow-md'
          ]"
          @dragover.prevent="onDragOver" 
          @dragleave.prevent="onDragLeave" 
          @drop.prevent="onDrop"
          @click="xlsxLoaded && fileInputRef?.click()"
        >
          <input type="file" ref="fileInputRef" class="hidden" accept=".xlsx, .xls, .csv" @change="handleFileInputChange" />
          
          <div class="bg-emerald-100 p-4 rounded-full mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
          </div>
          
          <h3 class="text-xl font-bold text-slate-800 mb-2">
            <span v-if="!xlsxLoaded">正在初始化本地引擎...</span>
            <span v-else>将 Excel 文件拖拽至此（支持多表或空表）</span>
          </h3>
          
          <!-- Trust Indicators -->
          <div class="flex flex-col items-center gap-2 mt-6 p-4 bg-slate-50 rounded-xl w-full">
            <div class="flex items-center text-emerald-700 font-medium text-sm">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-600"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg> 
              <span class="ml-1.5">您的完整文件不会上传至任何服务器</span>
            </div>
            <p class="text-xs text-slate-500">仅读取表头供 AI 理解结构，几十万行数据计算完全在您浏览器的内存中运行。</p>
          </div>
        </div>
      </div>

      <!-- Workspace -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left Panel: Command -->
        <div class="lg:col-span-4 flex flex-col space-y-4 h-[600px] lg:h-[calc(100vh-180px)]">
          
          <!-- File Info -->
          <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex justify-between items-center shrink-0">
            <div class="overflow-hidden">
              <p class="font-semibold text-slate-800 truncate text-sm">{{ fileName }}</p>
              <p class="text-xs text-slate-500 mt-0.5">共 {{ availableSheets.length }} 个工作表 | 纯本地处理</p>
            </div>
            <button 
              @click="closeFile"
              class="text-xs text-slate-400 hover:text-red-500 underline whitespace-nowrap ml-4"
            >
              关闭文件
            </button>
          </div>

          <!-- AI Command Box -->
          <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex-1 flex flex-col overflow-hidden">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2 mb-1 shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>
              告诉 AI 你想怎么处理
            </h3>
            <p class="text-xs text-slate-500 mb-3 shrink-0">操作将仅针对当前选中的工作表: <span class="font-semibold text-emerald-600">[{{ currentSheetName }}]</span></p>
            
            <!-- Shortcut Pills -->
            <div class="flex flex-wrap gap-2 mb-3 max-h-32 overflow-y-auto shrink-0">
              <button
                v-for="(s, idx) in SHORTCUTS"
                :key="idx"
                @click="prompt = s.prompt"
                class="text-[11px] px-2.5 py-1 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600 rounded-full border border-slate-200 transition-colors text-left"
              >
                {{ s.label }}
              </button>
            </div>

            <div class="flex-1 flex flex-col space-y-3 min-h-0 mt-1">
              <textarea
                class="flex-1 w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 resize-none text-sm transition-all"
                placeholder="输入指令（例如：帮我把地址列拆分，或者生成20条模拟用户数据...）"
                v-model="prompt"
                :disabled="isLoading"
              ></textarea>
              
              <!-- Trust indicator right near the execute button -->
              <div class="flex items-center justify-between shrink-0">
                <button 
                  @click="showPrivacyModal = true"
                  class="text-xs text-slate-400 hover:text-emerald-600 flex items-center transition-colors"
                  title="查看实际发送给AI的脱敏内容"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                  隐私透明度
                </button>

                <button
                  @click="handleProcess"
                  :disabled="isLoading || !prompt.trim()"
                  :class="[
                    'px-6 py-2 rounded-lg text-sm font-medium flex items-center transition-all',
                    isLoading || !prompt.trim() 
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                      : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm'
                  ]"
                >
                  <span v-if="isLoading">AI 处理中...</span>
                  <span v-else>针对当前表执行</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Panel: Data Table -->
        <div class="lg:col-span-8 flex flex-col h-[600px] lg:h-[calc(100vh-180px)]">
          <div class="flex-1 flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden transition-all">
            
            <!-- Status Bar -->
            <div class="px-4 py-3 border-b border-slate-200 flex justify-between items-center bg-white shrink-0">
              <h2 class="text-sm font-semibold text-slate-700 flex items-center gap-2">
                <span v-if="activeRecord?.isOriginal">原始数据</span>
                <span v-else>操作记录: {{ history.findIndex(h => h.id === activeHistoryId) }}</span>
              </h2>
              <div class="flex items-center gap-3">
                <span class="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
                  当前表共 {{ displayData.length }} 行
                </span>
                <button
                  @click="isHistoryDrawerOpen = true"
                  :class="[
                    'text-xs font-medium px-3 py-1.5 rounded-full flex items-center gap-1.5 transition-all duration-300 shadow-sm',
                    isNewRecordAdded
                      ? 'bg-emerald-500 text-white scale-105 shadow-emerald-500/40 animate-pulse'
                      : 'text-emerald-700 hover:text-emerald-800 bg-emerald-100 hover:bg-emerald-200'
                  ]"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l4 2"></path></svg>
                  工作簿历史 ({{ history.length }})
                </button>
              </div>
            </div>

            <!-- Sheet Tabs -->
            <div class="flex overflow-x-auto bg-slate-50 border-b border-slate-200 hide-scrollbar shrink-0">
              <button
                v-for="sheet in availableSheets"
                :key="sheet"
                @click="activeSheetName = sheet"
                :class="[
                  'flex items-center px-5 py-2.5 text-sm font-medium whitespace-nowrap transition-colors border-r border-slate-200',
                  currentSheetName === sheet 
                    ? 'bg-white text-emerald-700 border-t-2 border-t-emerald-500 shadow-[0_1px_0_0_white] z-10' 
                    : 'text-slate-500 hover:bg-slate-100 border-t-2 border-t-transparent'
                ]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 12 12 17 22 12"></polyline><polyline points="2 17 12 22 22 17"></polyline></svg>
                {{ sheet }}
              </button>
            </div>

            <!-- Table Data -->
            <div class="flex-1 overflow-auto bg-white">
              <table class="min-w-full divide-y divide-slate-200 text-sm">
                <thead class="bg-slate-50 sticky top-0 z-10 shadow-sm">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50 w-10 text-center border-r border-slate-200">#</th>
                    <th v-for="(col, idx) in displayColumns" :key="idx" class="px-3 py-2 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50 border-r border-slate-200 whitespace-nowrap">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-slate-200">
                  <tr v-for="(row, rowIdx) in displayData.slice(0, 100)" :key="rowIdx" class="hover:bg-slate-50 transition-colors">
                    <td class="px-3 py-1.5 text-xs text-slate-400 text-center border-r border-slate-200 bg-slate-50/50">
                      {{ rowIdx + 1 }}
                    </td>
                    <td v-for="(col, colIdx) in displayColumns" :key="colIdx" class="px-3 py-1.5 text-slate-700 border-r border-slate-200 whitespace-nowrap max-w-[200px] overflow-hidden text-ellipsis" :title="getCellValue(row, col)">
                      <span v-if="getCellValue(row, col)">{{ getCellValue(row, col) }}</span>
                      <span v-else class="text-slate-300">-</span>
                    </td>
                  </tr>
                  
                  <!-- 空数据状态提示 -->
                  <tr v-if="displayData.length === 0">
                    <td :colspan="Math.max(displayColumns.length + 1, 1)" class="px-3 py-20 text-center text-slate-500">
                      <div class="flex flex-col items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-emerald-300 mb-3"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>
                        <p class="font-medium text-slate-600 mb-1">【{{ currentSheetName }}】 暂无数据</p>
                        <p class="text-xs text-slate-400">您可以点击左侧快捷指令，让 AI 为您生成模拟数据测试。</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- --- Privacy Transparency Modal --- -->
      <div 
        v-if="showPrivacyModal"
        class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm transition-opacity"
        @click="showPrivacyModal = false"
      >
        <div 
          class="bg-slate-800 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden transform transition-all"
          @click.stop
        >
          <div class="px-5 py-4 border-b border-slate-700 flex justify-between items-center bg-slate-800/50">
            <h3 class="text-emerald-400 font-bold flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-400"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
              严格隐私模式验证
            </h3>
            <button 
              @click="showPrivacyModal = false"
              class="text-slate-400 hover:text-white transition-colors p-1 rounded-full hover:bg-slate-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
          <div class="p-6 text-slate-300 text-sm">
            <p class="mb-4">
              我们郑重承诺不会发送您的整个文件。为了让 AI 理解您的数据结构以编写处理逻辑，
              <span class="text-white font-bold bg-emerald-900/50 px-2 py-0.5 rounded ml-1">仅有以下极少量结构数据</span> 会被作为上下文发送：
            </p>
            <div class="bg-slate-950 p-4 rounded-lg overflow-x-auto border border-slate-700 shadow-inner">
              <pre class="text-xs leading-relaxed text-emerald-100 font-mono">{{ JSON.stringify(aiPayloadData, null, 2) }}</pre>
            </div>
            <div class="mt-5 flex items-start gap-2 text-slate-400 bg-slate-700/20 p-3 rounded-lg">
              <span class="text-xl">💡</span>
              <p class="text-xs leading-relaxed">
                表格中的所有其余数据均完全在您设备的本地内存中处理。即使您在此刻断开计算机的网络连接，只要 AI 代码已返回，庞大的数据处理依然可以瞬间完成。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- --- History Drawer UI --- -->
      <!-- Drawer Backdrop -->
      <div
        v-if="isHistoryDrawerOpen"
        class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 transition-opacity"
        @click="isHistoryDrawerOpen = false"
      ></div>

      <!-- Drawer Panel -->
      <div
        :class="[
          'fixed top-0 right-0 h-full w-80 md:w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col',
          isHistoryDrawerOpen ? 'translate-x-0' : 'translate-x-full'
        ]"
      >
        <div class="px-5 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <h3 class="text-base font-bold text-slate-800 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path><path d="M12 7v5l4 2"></path></svg>
            工作簿操作记录
          </h3>
          <button
            @click="isHistoryDrawerOpen = false"
            class="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-full hover:bg-slate-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
          <div
            v-for="(record, idx) in history"
            :key="record.id"
            @click="activeHistoryId = record.id"
            :class="[
              'p-3 rounded-xl border cursor-pointer transition-all',
              record.id === activeHistoryId
                ? 'bg-emerald-50 border-emerald-400 ring-2 ring-emerald-100 shadow-sm'
                : 'bg-white border-slate-200 hover:border-emerald-300 shadow-sm'
            ]"
          >
            <div class="flex justify-between items-start gap-2">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1.5">
                  <span v-if="record.id === activeHistoryId" class="flex h-2 w-2 rounded-full bg-emerald-500 shrink-0"></span>
                  <p :class="['text-sm font-semibold truncate', record.id === activeHistoryId ? 'text-emerald-800' : 'text-slate-700']">
                    <span v-if="record.isOriginal">{{ record.title }}</span>
                    <span v-else>操作记录 {{ idx }}</span>
                  </p>
                </div>
                <p v-if="!record.isOriginal" class="text-xs text-slate-600 line-clamp-2 mb-2" :title="record.title">
                  <span class="font-bold text-emerald-600 bg-emerald-100/50 px-1.5 py-0.5 rounded mr-1">
                    [{{ record.targetSheet }}]
                  </span>
                  {{ record.title }}
                </p>
                <p v-if="record.explanation" class="text-[11px] text-emerald-700 bg-emerald-100/50 p-2 rounded-md mt-1 leading-relaxed">
                  🤖 {{ record.explanation }}
                </p>
              </div>
              <div class="flex flex-col items-end shrink-0 gap-2">
                <span class="text-[10px] text-slate-400 font-medium">{{ record.timestamp }}</span>
                <button
                  v-if="!record.isOriginal"
                  @click.stop="handleDeleteHistory(record.id)"
                  class="text-slate-400 hover:text-red-500 transition-colors p-1 rounded hover:bg-red-50"
                  title="删除此记录"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

// --- Types ---
interface SheetData {
  data: any[];
  columns: string[];
}

interface HistoryRecord {
  id: string;
  title: string;
  targetSheet?: string;
  explanation?: string;
  sheets: Record<string, SheetData>;
  timestamp: string;
  isOriginal?: boolean;
}

// --- Prompt Shortcuts ---
const SHORTCUTS = [
  { label: "✨ 生成模拟数据", prompt: "请帮我生成20条员工测试数据，包含：姓名、手机号(11位数字)、所属部门(研发/销售/HR/财务)、入职时间(YYYY-MM-DD格式)、在职状态(在职/离职)。" },
  { label: "标准化日期", prompt: "检查所有包含日期的列，将其统一转换为 'YYYY-MM-DD' 格式。如果无法识别则保持原样。" },
  { label: "清理前后空格", prompt: "清除所有文本单元格内容前后的空格和不可见换行符。" },
  { label: "敏感信息打码", prompt: "识别包含手机号、身份证或邮箱的列，将中间部分用 '*' 号隐藏打码（例如手机号保留前3后4）。" },
  { label: "提取纯数字", prompt: "针对包含金额、价格或重量的列（如 '100元'，'50kg'），提取纯数字以便于后续计算。" },
  { label: "混合信息提取", prompt: "自动分析包含长文本的列，尝试提取出其中的人名、电话号码等关键信息，并存入新增加的列中。" },
  { label: "向下填充空白", prompt: "遍历所有列，如果遇到空白的单元格，使用它上方同列最近的一个非空单元格的值进行填充。" },
  { label: "多条件打标签", prompt: "请帮我根据特定的业务逻辑判定（例如某列数值大于一定阈值），新增一列 '用户标签' 并填入对应的分类结果。" },
  { label: "多列联合去重", prompt: "自动推断两到三列关键身份列（如姓名和手机号），基于组合进行排重，完全相同的只保留第一条数据。" },
  { label: "分组求和汇总", prompt: "根据某个维度列（如部门或分类）进行分组，并对其它包含数字的列进行求和汇总，生成全新的报表。" }
];

// --- State ---
const xlsxLoaded = ref(false);
const isDragging = ref(false);

const fileName = ref("");
const history = ref<HistoryRecord[]>([]);
const activeHistoryId = ref<string | null>(null);
const activeSheetName = ref("");

const isHistoryDrawerOpen = ref(false);
const isNewRecordAdded = ref(false);
const showPrivacyModal = ref(false);

const prompt = ref("");
const isLoading = ref(false);
const error = ref<string | null>(null);

const fileInputRef = ref<HTMLInputElement | null>(null);

// --- Derived State (Computed) ---
const activeRecord = computed(() => {
  return history.value.find(h => h.id === activeHistoryId.value) || history.value[0];
});

const availableSheets = computed(() => {
  return activeRecord.value?.sheets ? Object.keys(activeRecord.value.sheets) : [];
});

const currentSheetName = computed(() => {
  return availableSheets.value.includes(activeSheetName.value) 
    ? activeSheetName.value 
    : (availableSheets.value[0] || "");
});

const displayData = computed(() => {
  return activeRecord.value?.sheets?.[currentSheetName.value]?.data || [];
});

const displayColumns = computed(() => {
  return activeRecord.value?.sheets?.[currentSheetName.value]?.columns || [];
});

const aiPayloadData = computed(() => ({
  currentSheet: currentSheetName.value,
  columns: displayColumns.value,
  sampleRow: displayData.value[0] || {}
}));

// --- Lifecycle ---
onMounted(() => {
  if ((window as any).XLSX) {
    xlsxLoaded.value = true;
    return;
  }
  const script = document.createElement('script');
  script.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
  script.onload = () => { xlsxLoaded.value = true; };
  script.onerror = () => { error.value = "无法加载本地解析引擎，请检查网络。"; };
  document.head.appendChild(script);
});

// --- Methods ---
const closeFile = () => {
  history.value = [];
  activeHistoryId.value = null;
  fileName.value = "";
};

const handleFileInputChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    handleFileUpload(target.files[0]);
  }
  if (target) target.value = ''; // Reset to allow re-upload of same file
};

const handleFileUpload = (file: File) => {
  if (!file) return;
  const isExcel = file.name.match(/\.(xlsx|xls|csv)$/i);
  if (!isExcel) {
    error.value = "不支持的格式，请选择 .xlsx, .xls 或 .csv 文件";
    return;
  }

  fileName.value = file.name;
  error.value = null;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = e.target?.result;
      const workbook = (window as any).XLSX.read(data, { type: 'binary' });
      
      const initialSheets: Record<string, SheetData> = {};
      let firstSheet = "";

      workbook.SheetNames.forEach((sheetName: string, index: number) => {
        if (index === 0) firstSheet = sheetName;
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = (window as any).XLSX.utils.sheet_to_json(worksheet, { raw: false, defval: "" });
        initialSheets[sheetName] = {
          data: jsonData,
          columns: jsonData.length > 0 ? Object.keys(jsonData[0]) : []
        };
      });

      const initialRecord: HistoryRecord = {
        id: Date.now().toString(),
        title: "原始导入数据",
        sheets: initialSheets,
        timestamp: new Date().toLocaleTimeString(),
        isOriginal: true
      };
      
      history.value = [initialRecord];
      activeHistoryId.value = initialRecord.id;
      activeSheetName.value = firstSheet;
    } catch (err: any) {
      error.value = "解析时发生错误：" + err.message;
    }
  };
  reader.readAsBinaryString(file);
};

const onDragOver = () => { isDragging.value = true; };
const onDragLeave = () => { isDragging.value = false; };
const onDrop = (e: DragEvent) => {
  isDragging.value = false;
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    handleFileUpload(e.dataTransfer.files[0]);
  }
};

const handleProcess = async () => {
  if (!prompt.value.trim()) return; 
  isLoading.value = true;
  error.value = null;

  try {
    const apiKey = ""; // 请在此处填入您的 API Key 或通过环境变量注入
    
    const systemInstruction = `You are a strict, expert JavaScript data transformation assistant.
Task: Write a single JS function 'transform(data)' to transform an array of objects based on user command.
Context sent by user (Focusing ONLY on sheet: '${currentSheetName.value}'):
- Columns: ${JSON.stringify(aiPayloadData.value.columns)}
- Sample 1st Row: ${JSON.stringify(aiPayloadData.value.sampleRow)}

Rules:
1. Return purely a valid JSON object: {"code": "function transform(data) {...return newData;}", "explanation": "Brief Chinese explanation"}.
2. Use ES6+ pure JS. NO external libraries. Handle missing keys gracefully.
3. Your code will run locally on the user's FULL dataset. Return a deeply cloned and modified array.
4. IMPORTANT: If the input 'data' is empty and the user asks to generate mock/test data, generate and return a new array of objects fulfilling their request.`;

    const payload = {
      contents: [{ parts: [{ text: `User Command: ${prompt.value}` }] }],
      systemInstruction: { parts: [{ text: systemInstruction }] },
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: { code: { type: "STRING" }, explanation: { type: "STRING" } },
          required: ["code", "explanation"]
        }
      }
    };

    let result;
    for (let i = 0; i < 3; i++) {
      try {
        const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
          method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)
        });
        if (res.ok) { result = await res.json(); break; }
      } catch (e) { if (i === 2) throw e; }
    }

    const aiText = result?.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!aiText) throw new Error("AI 响应失败。");
    
    const parsed = JSON.parse(aiText);
    
    // Sandbox execution on current sheet data
    const executionWrapper = new Function('data', `${parsed.code}\n return transform(data);`);
    const dataCopy = JSON.parse(JSON.stringify(displayData.value));
    const transformedData = executionWrapper(dataCopy);

    if (!Array.isArray(transformedData)) throw new Error("处理结果格式异常，期望返回数组。");

    const keySet = new Set<string>();
    transformedData.forEach(row => Object.keys(row).forEach(k => keySet.add(k)));

    // 深拷贝当前所有的 Sheet 状态
    const newSheetsSnapshot = JSON.parse(JSON.stringify(activeRecord.value.sheets));
    newSheetsSnapshot[currentSheetName.value] = {
      data: transformedData,
      columns: Array.from(keySet)
    };

    const newRecord: HistoryRecord = {
      id: Date.now().toString(),
      title: prompt.value,
      targetSheet: currentSheetName.value,
      explanation: parsed.explanation,
      sheets: newSheetsSnapshot,
      timestamp: new Date().toLocaleTimeString()
    };

    history.value.push(newRecord);
    activeHistoryId.value = newRecord.id;
    prompt.value = "";
    
    isNewRecordAdded.value = true;
    setTimeout(() => { isNewRecordAdded.value = false; }, 2000);

  } catch (err: any) {
    error.value = "执行失败: " + (err.message || "未知错误");
  } finally {
    isLoading.value = false;
  }
};

const handleDeleteHistory = (id: string) => {
  const filtered = history.value.filter(h => h.id !== id);
  if (activeHistoryId.value === id && filtered.length > 0) {
    activeHistoryId.value = filtered[filtered.length - 1].id;
  }
  history.value = filtered;
};

const handleDownload = () => {
  if (!(window as any).XLSX || !activeRecord.value) return; 
  try {
    const workbook = (window as any).XLSX.utils.book_new();
    
    Object.entries(activeRecord.value.sheets).forEach(([sheetName, sheetContent]) => {
      const dataToExport = (sheetContent as SheetData).data;
      const worksheet = (window as any).XLSX.utils.json_to_sheet(dataToExport.length > 0 ? dataToExport : []);
      (window as any).XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
    });
    
    const exportName = fileName.value ? fileName.value.replace(/\.[^/.]+$/, "") + "_已处理" : "数据导出";
    (window as any).XLSX.writeFile(workbook, `${exportName}.xlsx`);
  } catch (err: any) { 
    error.value = "导出失败: " + err.message; 
  }
};

const getCellValue = (row: any, col: string): string => {
  let cellValue = row[col];
  if (typeof cellValue === 'object' && cellValue !== null) {
    cellValue = JSON.stringify(cellValue);
  }
  return cellValue !== undefined && cellValue !== null && cellValue !== "" ? String(cellValue) : "";
};
</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
```
