<template>
    <el-dialog v-model="internalVisible" title="Upload File" width="500" center>
        <el-upload class="upload-demo" drag :action="uploadAction" :accept="acceptedFileTypes" :auto-upload="false"
            :before-upload="beforeUpload" :on-success="handleSuccess" :on-error="handleError" :limit="1"
            v-model:file-list="fileList">
            <el-icon class="el-icon--upload">
                <upload-filled />
            </el-icon>
            <div class="el-upload__text">
                Drop document files here or <em>click to upload</em>
            </div>
            <template #tip>
                <div class="el-upload__tip">
                    Supported document types: pdf, doc, docx, ppt, pptx, xls, xlsx, txt (max size: {{ maxSizeInMB }} MB)
                </div>
            </template>

        </el-upload>
        <el-row class="row-bg" justify="space-evenly">
            <el-button class="ml-5" type="primary" @click="handleConfirm">
                upload to server
            </el-button>
        </el-row>

    </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue';
import documentService from '@/services/documentService';

const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true
    },
    uploadAction: {
        type: String,
        required: true
    },
    acceptedFileTypes: {
        type: String,
        required: true
    },
    maxSizeInMB: {
        type: Number,
        required: true
    }
});
const emit = defineEmits(['update:modelValue', 'file-uploaded']);

const internalVisible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

const fileList = ref([]);


async function handleConfirm() {
    if (fileList.value.length === 0) {
        ElMessage.warning('Please select a file before uploading.');
        return;
    }
    try {
        const formData = new FormData();
        formData.append('file', fileList.value[0].raw); // Ensure the file is appended with the key 'file'
        const response = await documentService.uploadDocument(formData);
        handleSuccess(response);
    } catch (error) {
        handleError(error, fileList.value[0], fileList.value);
    }
}

function handleExceed(files, fileList) {
    ElMessage.warning('Only one file can be uploaded at a time.');
}

function beforeUpload(file) {
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (!isLt2M) {
        ElMessage.error('File size cannot exceed 2MB!');
    }
    return isLt2M;
}

function handleSuccess(response) {
    if (response.message) {
        ElMessage.success(response.message);
    } else {
        ElMessage.error(response.error);
    }
    emit('file-uploaded', response);
    fileList.value = [];
    internalVisible.value = false;
}

function handleError(err, file, fileListParam) {
    if (err.response && err.response.data && err.response.data.error) {
        ElMessage.error(err.response.data.error);
    } else {
        ElMessage.error('Upload failed, please try again.');
    }
    console.error('Upload failed:', err);
}
</script>

<style scoped>
.upload-demo {
    margin-bottom: 20px;
}

.dialog-footer {
    text-align: right;
}
</style>