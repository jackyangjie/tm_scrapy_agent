export default {
    customRequest(options) {
        // 模拟上传进度
        options.onProgress({
            percent: 100,
        });
        // 当前是一个 mock 的上传行为
        // 实际情况需要具体实现一个文件上传服务，将文件转化为 url
        options.onSuccess({
            url: URL.createObjectURL(options.file as Blob)
        });
    }
} 