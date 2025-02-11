import axios from 'axios'

const API_BASE_URL = `${import.meta.env.VITE_BASE_URL}`

export default {
  async uploadDocument(file) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
  async getDocuments() {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents`)
      console.log(response.data)
      return response.data
    } catch (error) {
      // You can add more detailed error handling here if needed.
      throw error
    }
  }
}
