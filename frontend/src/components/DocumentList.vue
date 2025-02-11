<template>
    <el-container class="documents-page">
        <!-- Header -->
        <el-header class="header">
            <h2>Documents Manager</h2>
        </el-header>

        <!-- Main Content -->
        <el-main class="content">
            <UploadModal v-model="showUploadModal" uploadAction="/upload" acceptedFileTypes="image/*,application/pdf"
                :maxSizeInMB="10" @file-uploaded="handleUploadSuccess" @upload-error="handleUploadError" />
            <div class="toolbar">
                <!-- Filter Section (Left) -->
                <div class="filter-section">
                    <el-form inline class="filter-form">
                        <el-form-item label="File Name">
                            <el-input v-model="searchName" placeholder="Search by file name" clearable
                                data-testid="search-name" />
                        </el-form-item>
                        <el-form-item label="Category">
                            <el-select-v2 v-model="selectedCategory" :options="categoryOptions"
                                placeholder="Search by category" clearable style="width: 240px" multiple />
                        </el-form-item>

                    </el-form>
                </div>
                <div class="upload-section">
                    <el-button type="primary" @click="openModal" data-testid="upload-button">
                        <i class="el-icon-upload"></i> Upload New File
                    </el-button>
                </div>
            </div>

            <el-table :data="filteredDocuments" stripe v-loading="loading" element-loading-text="Loading..."
                class="document-table" data-testid="document-table">
                <el-table-column prop="fileName" label="File Name" />
                <el-table-column prop="upload_time" label="Upload Time" />
                <el-table-column prop="fileSize" label="Size" />
                <el-table-column label="Category">
                    <template #default="scope">
                        <span v-if="scope.row.category != 'none'">{{ scope.row.category }}</span>
                        <template v-else>
                            <el-button v-if="!loading" type="warning" @click="analyzeDocument(scope.$index, scope.row)"
                                data-testid="analyze-button">
                                Analyze
                            </el-button>
                            <el-icon v-else>
                                <i class="el-icon-loading"></i> Fetching...
                            </el-icon>
                        </template>
                    </template>
                </el-table-column>
                <el-table-column label="Actions">
                    <template #default="scope">
                        <el-button type="danger" @click="handleDelete(scope.$index, scope.row)"
                            data-testid="delete-button">
                            Delete
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-main>


        <!-- Upload File Modal -->

    </el-container>
</template>

<script setup lang="ts">
import UploadModal from '../components/UploadFileModal.vue'
import { onMounted, watch, ref } from 'vue';
import { ElMessage, ElMessageBox, ElContainer, ElButton, ElTable, ElHeader, ElInput, ElTableColumn, ElMain, ElForm, ElFormItem, ElSelectV2 } from 'element-plus';
import documentService from '@/services/documentService';

// Variables

const selectedCategory = ref('');
const loading = ref(true);
const searchName = ref('');
const selectedCategories = ref([]);
const showUploadModal = ref(false)

const visible = ref(true);
let filteredDocuments = ref<Document[]>([]);
interface Document {
    fileName: string;
    category: string;
    upload_time: string;
    fileSize: string;
    documentId: string;
}

// New function to transform the provided data
function transformDocumentData(data: any): Document {
    return {
        fileName: data.metadata.original_name,
        category: data.metadata.category,
        upload_time: data.metadata.upload_time,
        fileSize: `${(data.size / 1024).toFixed(2)} KB`, // Convert size to KB
        documentId: data.filename
    };
}

const documentList = ref<Document[]>([]);
const categoryOptions = ref([]);

watch(selectedCategory, (newValue) => {
    if (!newValue || newValue.length === 0) {
        filteredDocuments.value = documentList.value;
        return;
    }
    filteredDocuments.value = documentList.value.filter((item) => {
        return newValue.includes(item.category);
    });
});

function updateCategoryOptions() {
    const uniqueCategories = new Set(documentList.value.map(doc => doc.category));
    categoryOptions.value = Array.from(uniqueCategories).map(category => ({
        label: category,
        value: category
    }));
}

// functions
const analyzeDocument = async (index: number, row: Document) => {
    let documentId = row.documentId;
    try {
        let category = await documentService.analyzeDocument(documentId);
        filteredDocuments.value[index].category = category.detected_category;
        ElMessage.success('Document detected successfully!');
    } catch (error) {
        ElMessage.error('Failed to analyze document.');
        console.error('Error analyzing document:', error);
    }
};

const handleDelete = (index: number, row: Document) => {
    ElMessageBox.confirm(
        `Are you sure you want to delete the document: ${row.fileName}?`,
        'Confirm Delete',
        {
            confirmButtonText: 'Delete',
            cancelButtonText: 'Cancel',
            type: 'warning',
        }
    ).then(async () => {
        try {
            await documentService.deleteDocument(row.documentId);
            filteredDocuments.value.splice(index, 1);
            ElMessage.success('Document deleted successfully!');
        } catch (error) {
            ElMessage.error('Failed to delete document.');
            console.error('Error deleting document:', error);
        }
    }).catch(() => {
        ElMessage.info('Delete canceled');
    });

};
function handleUploadSuccess(response) {
    // Handle the successful upload (e.g. update the UI or state)
    ElMessage.success('Document uploaded successfully!')
}

function handleUploadError(error) {
    // Handle the error case as needed
    ElMessage.error('Document upload failed.')
    console.error('Upload error:', error)
}
function openModal() {
    showUploadModal.value = true
}
async function fetchDocumentList() {
    loading.value = true;
    documentList.value = await documentService.getDocuments();
    const transformedDocuments = documentList.value.map(transformDocumentData);
    documentList.value = transformedDocuments;
    filteredDocuments.value = transformedDocuments;
    updateCategoryOptions()
    loading.value = false;
}
// Watchers
onMounted(async () => {
    try {
        fetchDocumentList()
    } catch (error) {
        ElMessage.error('Failed to fetch documents.');
        console.error('Error fetching documents:', error);
    }
});

watch(searchName, (newValue) => {
    if (!newValue || newValue === '') {
        filteredDocuments.value = documentList.value;
        return;
    }
    else
        filteredDocuments.value = documentList.value.filter((item) => {
            return item.fileName.includes(newValue);
        });
});
</script>
<style scoped>
.documents-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.header {
    background-color: #409EFF;
    color: #fff;
    text-align: center;
}

.content {
    flex: 15;
    padding: 20px;
    background: #f0f2f5;
}

.toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    background: #fff;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-section {
    display: flex;
    align-items: center;
}

.filter-form .el-form-item {
    margin-right: 20px;
}

.document-table {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Footer Styles */
.footer {
    text-align: center;
    padding: 10px;
    background-color: #f5f5f5;
}
</style>