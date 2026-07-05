# 基于函数计算和FFmpeg处理音视频

使用Serverless Devs开发工具可以快速部署基于函数计算、对象存储OSS和FFmpeg的应用，帮助您处理音视频，例如获取音视频信息、给音视频添加水印及转换格式等。

## 背景信息

FFmpeg是一套可以记录、转换数字音视频，并将其转化为流的开源计算机程序。FFmpeg采用LGPL或GPL许可证，提供了录制、转换和流化音视频的完整解决方案，包括先进的音视频编解码库libavcodec，并且保证了高可移植性和编解码质量。详细信息，请参见[FFmpeg](https://ffmpeg.org/documentation.html)。

本文以Python语言为例，介绍的示例模板中包含以下主题。您也可以根据实际需求修改给到示例的函数代码实现二次开发。

| **示例名称** | **描述** |
| --- | --- |
| GetMediaMeta | 获取音视频的Meta信息。 |
| GetDuration | 获取音视频的时长。 |
| GetSprites | 将视频制作成雪碧图。 |
| VideoWatermark | 添加文字水印、静态图片水印和动态GIF水印。 |
| AudioConvert | 转换音视频格式。 |
| VideoGif | 将Video格式提取成GIF格式。 |

## 前提条件

您已完成以下操作：

1. [开通函数计算](https://help.aliyun.com/zh/functioncompute/fc/use-event-functions-to-handle-oss-file-upload-events)
2. [创建对象存储Bucket](https://help.aliyun.com/zh/oss/user-guide/create-a-bucket-4#concept-ntj-wx1-5db)
3. [安装Serverless Devs和Docker](https://help.aliyun.com/zh/functioncompute/fc-2-0/developer-reference/install-serverless-devs-and-docker#task-2093092)
4. [配置Serverless Devs](https://help.aliyun.com/zh/functioncompute/fc-2-0/developer-reference/configure-serverless-devs#task-2093369)

## 使用Serverless Devs部署应用

1. 执行以下命令，初始化项目。
  
  ```
  sudo s init ffmpeg-app-v3 -d ffmpeg-app-v3
  ```
  
  `-d`用于指定生成的目录的名称。
2. 执行以下命令，进入项目目录。
  
  ```
  cd ffmpeg-app-v3
  ```
3. **可选：**您可以按需修改项目目录中的代码示例，实现您的业务逻辑。
4. 执行以下命令，部署项目。
  
  ```
  sudo s deploy -y
  ```
  
  **
  
  **说明**
  
  如果您只需要部署该项目内的某个功能，例如需要部署GetMediaMeta功能获取音视频的Meta信息。请执行以下命令：
  
  ```
  sudo s GetMediaMeta deploy
  ```
  
  当您需要部署其他功能时，请将`GetMediaMeta`修改为其他功能的名称。
  
  **部署完成后，输出示例如下。**
  
  ```
  Downloading[/v3/packages/fc3/zipball/0.0.47]... Download fc3 successfully Steps for [deploy] of [ffmpeg-app] ==================== Downloading[/v3/packages/fc3-domain/zipball/0.0.23]... Download fc3-domain successfully TIPS: You can use "s info" get more detail ✔ [AudioConvert] completed (2.19s) ✔ [GetMediaMeta] completed (0.85s) ✔ [GetDuration] completed (0.78s) ✔ [VideoGif] completed (0.77s) ✔ [GetSprites] completed (0.71s) ✔ [VideoWatermark] completed (0.82s) Result for [deploy] of [ffmpeg-app] ==================== AudioConvert: region: cn-hangzhou description: 音频格式转换器 functionArn: acs:fc:cn-hangzhou:************0898:functions/AudioConvert-**** functionName: AudioConvert-**** handler: index.handler internetAccess: true memorySize: 1024 role: acs:ram::************0898:role/aliyunfcdefaultrole runtime: python3.9 timeout: 900 __component: fc3 GetMediaMeta: region: cn-hangzhou description: 获取音视频 meta functionArn: acs:fc:cn-hangzhou:************0898:functions/GetMediaMeta-**** functionName: GetMediaMeta-**** handler: index.handler internetAccess: true memorySize: 1024 role: acs:ram::************0898:role/aliyunfcdefaultrole runtime: python3.9 timeout: 900 __component: fc3 GetDuration: region: cn-hangzhou description: 获取音视频时长 functionArn: acs:fc:cn-hangzhou:************0898:functions/GetDuration-**** functionName: GetDuration-**** handler: index.handler internetAccess: true memorySize: 1024 role: acs:ram::************0898:role/aliyunfcdefaultrole runtime: python3.9 timeout: 900 __component: fc3 VideoGif: region: cn-hangzhou description: 功能强大的 video 提取为 gif 函数 functionArn: acs:fc:cn-hangzhou:************0898:functions/VideoGif-**** functionName: VideoGif-**** handler: index.handler internetAccess: true memorySize: 1024 role: acs:ram::************0898:role/aliyunfcdefaultrole runtime: python3.9 timeout: 900 __component: fc3 GetSprites: region: cn-hangzhou description: 功能强大雪碧图制作函数 functionArn: acs:fc:cn-hangzhou:************0898:functions/GetSprites-**** functionName: GetSprites-**** handler: index.handler internetAccess: true memorySize: 1024 role: acs:ram::************0898:role/aliyunfcdefaultrole runtime: python3.9 timeout: 900 __component: fc3 VideoWatermark: region: cn-hangzhou description: 功能强大的视频添加水印功能 functionArn: acs:fc:cn-hangzhou:************0898:functions/VideoWatermark-**** functionName: VideoWatermark-**** handler: index.handler internetAccess: true memorySize: 1024 role: acs:ram::************0898:role/aliyunfcdefaultrole runtime: python3.9 timeout: 900 __component: fc3
  ```
5. 调用示例函数。
  
  **调用GetMediaMeta函数，获取音视频的Meta信息**
  
  调用GetMediaMeta函数的示例命令如下，请根据实际情况修改参数信息。
  
  ```
  sudo s GetMediaMeta invoke -e '{"bucket_name": "test-bucket","object_key": "a.mp4"}'
  ```
  
  **参数说明：**
  
  - `bucket_name`：Bucket名称。
  - `object_key`：需获取音视频Meta信息的文件的名称。
  
  **输出示例：**
  
  ```
  Steps for [invoke] of [ffmpeg-app] ==================== ========= FC invoke Logs begin ========= FunctionCompute python3 runtime inited. FC Invoke Start RequestId: 1-67051746-15265ec4-4fa70b****** 2024-10-08T11:28:07.836Z 1-67051746-15265ec4-4fa70b****** [INFO] current Function [handler] excute time is 0.46 seconds FC Invoke End RequestId: 1-67051746-15265ec4-4fa70b****** Duration: 891.57 ms, Billed Duration: 892 ms, Memory Size: 1024 MB, Max Memory Used: 60.01 MB ========= FC invoke Logs end ========= Invoke instanceId: c-67051746-152fc2e0-b08240****** Code Checksum: 3393206491906161454 Qualifier: LATEST RequestId: 1-67051746-15265ec4-4fa70b****** Invoke Result: { "format": { "bit_rate": "17024829", "duration": "110.037333", "filename": "http://test-bucket.oss-cn-hangzhou-internal.aliyuncs.com/a.mp4......", "format_long_name": "QuickTime / MOV", "format_name": "mov,mp4,m4a,3gp,3g2,mj2", "nb_programs": 0, "nb_streams": 2, "probe_score": 100, "size": "234170850", "start_time": "0.000000", "tags": { "compatible_brands": "mp42mp41", "creation_time": "2020-09-05T06:03:49.000000Z", "major_brand": "mp42", "minor_version": "0" } }, "streams": [ { "avg_frame_rate": "25/1", "bit_rate": "16708594", "bits_per_raw_sample": "8", "chroma_location": "left", "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10", "codec_name": "h264", "codec_tag": "0x31637661", "codec_tag_string": "avc1", "codec_time_base": "1/50", "codec_type": "video", "coded_height": 1088, "coded_width": 1920, "color_primaries": "bt709", "color_range": "tv", "color_space": "bt709", "color_transfer": "bt709", "disposition": { "attached_pic": 0, "clean_effects": 0, "comment": 0, "default": 1, "dub": 0, "forced": 0, "hearing_impaired": 0, "karaoke": 0, "lyrics": 0, "original": 0, "timed_thumbnails": 0, "visual_impaired": 0 }, "duration": "110.000000", "duration_ts": 2750000, "has_b_frames": 1, "height": 1080, "index": 0, "is_avc": "true", "level": 41, "nal_length_size": "4", "nb_frames": "2750", "pix_fmt": "yuv420p", "profile": "Main", "r_frame_rate": "25/1", "refs": 1, "start_pts": 0, "start_time": "0.000000", "tags": { "creation_time": "2020-09-05T06:03:49.000000Z", "encoder": "AVC Coding", "handler_name": "\u001fMainconcept Video Media Handler", "language": "eng" }, "time_base": "1/25000", "width": 1920 }, { "avg_frame_rate": "0/0", "bit_rate": "317375", "bits_per_sample": 0, "channel_layout": "stereo", "channels": 2, "codec_long_name": "AAC (Advanced Audio Coding)", "codec_name": "aac", "codec_tag": "0x6134706d", "codec_tag_string": "mp4a", "codec_time_base": "1/48000", "codec_type": "audio", "disposition": { "attached_pic": 0, "clean_effects": 0, "comment": 0, "default": 1, "dub": 0, "forced": 0, "hearing_impaired": 0, "karaoke": 0, "lyrics": 0, "original": 0, "timed_thumbnails": 0, "visual_impaired": 0 }, "duration": "110.000000", "duration_ts": 5280000, "index": 1, "max_bit_rate": "417750", "nb_frames": "5158", "profile": "LC", "r_frame_rate": "0/0", "sample_fmt": "fltp", "sample_rate": "48000", "start_pts": 0, "start_time": "0.000000", "tags": { "creation_time": "2020-09-05T06:03:49.000000Z", "handler_name": "#Mainconcept MP4 Sound Media Handler", "language": "eng" }, "time_base": "1/48000" } ] } End of method: invoke
  ```
  
  **调用GetDuration函数，获取音视频的时长**
  
  调用GetDuration函数的示例命令如下，请根据实际情况修改参数信息。
  
  ```
  sudo s GetDuration invoke -e '{"bucket_name": "bucket-name","object_key": "a.mp4"}'
  ```
  
  **参数说明：**
  
  - `bucket_name`：Bucket名称。
  - `object_key`：需获取时长的文件的名称。
  
  **输出示例：**
  
  ```
  Steps for [invoke] of [ffmpeg-app] ==================== ========= FC invoke Logs begin ========= FunctionCompute python3 runtime inited. FC Invoke Start RequestId: 1-67051470-15a07456-27998a****** 2024-10-08T11:16:03.069Z 1-67051470-15a07456-27998a****** [INFO] current Function [handler] excute time is 0.46 seconds FC Invoke End RequestId: 1-67051470-15a07456-27998a****** Duration: 866.68 ms, Billed Duration: 867 ms, Memory Size: 1024 MB, Max Memory Used: 60.00 MB ========= FC invoke Logs end ========= Invoke instanceId: c-67051470-152fc2e0-782287****** Code Checksum: 6541531297040229118 Qualifier: LATEST RequestId: 1-67051470-15a07456-27998a****** Invoke Result: 18.416667 [GetDuration] completed (2.67s)
  ```
  
  **调用GetSprites函数，将视频制作成雪碧图**
  
  调用GetSprites函数的示例命令如下，请根据实际情况修改参数信息。
  
  ```
  sudo s GetSprites invoke -e '{"bucket_name": "test-bucket","object_key": "a.mp4", "output_dir" : "output/", "tile": "3*4"}'
  ```
  
  **参数说明：**
  
  - `bucket_name`：Bucket的名称。
  - `object_key`：需制作成雪碧图的文件的名称。
  - `output_dir`：转码后的视频存储在Bucket内的位置。
  - `tile`：雪碧图的行和列。
  - （可选）`start`：开始制作雪碧图的时间。默认值为0。
  - （可选）`duration`：基于Start参数后多长时间的视频内开始截图。例如start取值为10，duration取值为20，表示截取10s到30s内的视频。
  - （可选）`itsoffset`：表示流偏移命令，延迟时间。默认值为0。该参数需要和start、interval一起使用，示例如下：
    
    - `start`取值为0，`interval`取值为10，`itsoffset`取值为0，则截图的描述为5、15和25等。
    - `start`取值为0，`interval`取值为10，`itsoffset`取值为1，则截图的描述为4、14和24等。
    - `start`取值为0，`interval`取值为10，`itsoffset`取值为-1，则截图的描述为6、16和26等。
    - `start`取值为0，`interval`取值为10，`itsoffset`取值为4.999，则截图的描述为0、10和20等。
    
    **
    
    **说明**
    
    当该参数取值为5时，会丢失0秒时的图片，建议您将该参数设置为4.999。
  - （可选）`scale`：截图的大小。默认比例为-1:-1。
  - （可选）`interval`：表示时隔几秒截取一次视频。默认值为1。
  - （可选）`padding`：表示图片的间隔。默认值为0。
  - （可选）`color`：表示雪碧图的背景颜色。默认颜色为黑色。
  - （可选）`dst_type`：表示生成雪碧图的图片格式。默认为JPG。取值为JPG和PNG。
  
  **输出示例：**
  
  ```
  Steps for [invoke] of [ffmpeg-app] ==================== ========= FC invoke Logs begin ========= yuvj420p(pc), 11520x8640, q=2-31, 200 kb/s, 0.08 fps, 0.08 tbn, 0.08 tbc (default)\n Metadata:\n creation_time : 2024-10-08T06:45:29.000000Z\n handler_name : Core Media Video\n encoder : Lavc58.54.100 mjpeg\n Side data:\n cpb: bitrate max/min/avg: 0/0/200000 buffer size: 0 vbv_delay: -1\nframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 0 fps=0.0 q=0.0 size=N/A time=00:00:00.00 bitrate=N/A speed= 0x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=1.21x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=1.15x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed= 1.1x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=1.05x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=1.01x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.966x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.923x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.887x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.855x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.822x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.794x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.768x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.736x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.714x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.693x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.673x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.652x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.634x \rframe= 1 fps=0.1 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.615x \rframe= 1 fps=0.0 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.597x \rframe= 1 fps=0.0 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.582x \rframe= 1 fps=0.0 q=21.1 size=N/A time=00:00:12.00 bitrate=N/A speed=0.566x \r[mjpeg @ 0x464b0c0] get_buffer() failed\n[mjpeg @ 0x464b0c0] thread_get_buffer() failed\n[mjpeg @ 0x464b0c0] get_buffer() failed (-12 (nil))\nVideo encoding failed\nConversion failed!\n" 2024-10-08T11:16:59.390Z 1-67051494-15cef74d-1880b1****** [ERROR] stdout:b'' 2024-10-08T11:16:59.540Z 1-67051494-15cef74d-1880b1****** [INFO] Uploaded /tmp/screen.record1.jpg to output/screen.record1.jpg 2024-10-08T11:16:59.540Z 1-67051494-15cef74d-1880b1****** [INFO] current Function [handler] excute time is 22.28 seconds FC Invoke End RequestId: 1-67051494-15cef74d-1880b1****** Duration: 22703.61 ms, Billed Duration: 22704 ms, Memory Size: 1024 MB, Max Memory Used: 926.45 MB ========= FC invoke Logs end ========= Invoke instanceId: c-67051494-152fc2e0-aecae7****** Code Checksum: 3870681690589467457 Qualifier: LATEST RequestId: 1-67051494-15cef74d-1880b1****** Invoke Result: ok [GetSprites] completed (23.38s)
  ```
  
  **调用VideoWatermark函数，给视频添加水印**
  
  调用VideoWatermark函数的示例命令如下，请根据实际情况修改参数信息。
  
  ```
  sudo s VideoWatermark invoke -e '{"bucket_name": "test-bucket","object_key": "a.mp4", "output_dir" : "output/", "vf_args" : "drawtext=fontfile=/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc:text='hello函数计算':x=100:y=50:fontsize=24:fontcolor=red"}'
  ```
  
  **参数说明：**
  
  - `bucket_name`：Bucket的名称。
  - `object_key`：需添加水印的文件的名称。
  - `output_dir`：转码后的视频存储在Bucket内的位置。
  - `vf_args`：表示文字水印或静态图片水印。
  - `filter_complex_args`：表示动态图片水印。当设置该参数与`vf_args`同时设置时，则默认忽略`vf_args`的参数信息。
  
  **输出示例：**
  
  ```
  Steps for [invoke] of [ffmpeg-app] ========= FC invoke Logs begin ========= static-master/target/lib ...... ...... FC Invoke End RequestId: 31ecddfa-4e41-44bb-9489-00708b07**** Duration: 3740.74 ms, Billed Duration: 3741 ms, Memory Size: 1024 MB, Max Memory Used: 979.74 MB ========= FC invoke Logs end ========= Invoke instanceId: c-67051514-152fc2e0-7ca0b5****** Code Checksum: 15811305094477563349 Qualifier: LATEST RequestId: 1-67051514-15f4ad6f-b9e770****** Invoke Result: ok [VideoWatermark] completed (7.04s)
  ```
  
  **调用AudioConvert函数，转换音频格式**
  
  调用AudioConvert函数的示例命令如下，请根据实际情况修改参数信息。
  
  ```
  sudo s AudioConvert invoke -e '{"bucket_name": "test-bucket","object_key": "a.mp4", "output_dir" : "output/", "dst_type":".wav", "ac":"1", "ar":"4000"}'
  ```
  
  **参数说明：**
  
  - `bucket_name`：Bucket的名称。
  - `object_key`：需转换音频格式的文件的名称。
  - `output_dir`：转码后的视频存储在Bucket内的位置。
  - `dst_type`：转换后文件的格式。
  - （可选）`ac`：指定声道数。
  - （可选）`ar`：指定采样率。
  
  **输出示例：**
  
  ```
  Steps for [invoke] of [ffmpeg-app] ========= FC invoke Logs begin ========= ...... 2024-10-08T11:19:14.345Z 1-67051531-1540ac27-5efd5d****** [INFO] current Function [handler] excute time is 0.39 seconds FC Invoke End RequestId: 1-67051531-1540ac27-5efd5d****** Duration: 1156.09 ms, Billed Duration: 1157 ms, Memory Size: 256 MB, Max Memory Used: 88.23 MB ========= FC invoke Logs end ========= FC Invoke Result: ok End of method: invoke
  ```
  
  **调用VideoGif函数，为视频提取GIF**
  
  调用VideoGif函数的示例命令如下，请根据实际情况修改参数信息。
  
  ```
  sudo s VideoGif invoke -e '{"bucket_name": "test-bucket","object_key": "a.mp4", "output_dir" : "output/", "vframes": "5", "start": "0", "duration": "2"}'
  ```
  
  **参数说明：**
  
  - `bucket_name`：Bucket的名称。
  - `object_key`：需转换为GIF格式的文件的名称。
  - `output_dir`：转码后的视频存储在对象存储中的位置。
  - （可选）`vframes`：基于`start`参数后多长时间的视频内开始转换视频。
  - （可选）`start`：开始转换的时间。默认值为0。
  - （可选）`duration`：基于`start`参数后多长时间的视频内开始转换视频。
  
  **
  
  **说明**
  
  当同时设置了`duration`和`vframes`参数时，以`duration`的参数信息为准。当这两个参数都未设置时，则默认将整个视频转换为GIF格式。
  
  **输出示例：**
  
  ```
  Steps for [invoke] of [ffmpeg-app] ========= FC invoke Logs begin ========= FunctionCompute python3 runtime inited. FC Invoke Start RequestId: 1-6705158b-15aae364-e8b091****** 2024-10-08T11:20:48.472Z 1-6705158b-15aae364-e8b091****** [INFO] b'{"bucket_name": "csy-test-bucket-hangzhou","object_key": "screen.record.mov", "output_dir" : "output/", "vframes": "5", "start": "0", "duration": "2"}' 2024-10-08T11:20:48.553Z 1-6705158b-15aae364-e8b091****** [INFO] cmd = ffmpeg -y -ss 0 -t 2 -accurate_seek -i http://csy-test-bucket-hangzhou.oss-cn-hangzhou-internal.aliyuncs.com/screen.record.mov?security-token=CAISzgJ1q6Ft5B2yfSjIr5bgJd%2BBj5FX%2FbSlR3HinW8hR95tobDlkzz2IHhMe3JhAuwdtPw0lG1Y5vgYlqZdVplOWU3Da%2BB364xK7Q75%2FH00TwPvv9I%2Bk5SANTW5KXyShb3%2FAYjQSNfaZY3eCTTtnTNyxr3XbCirW0ffX7SClZ9gaKZ8PGD6F00kYu1bPQx%2FssQXGGLMPPK2SH7Qj3HXEVBjt3gX6wo9y9zmmZfDs0CA1AenkLVN99WhGPX%2BMZkwZqUYesyuwel7epDG1CNt8BVQ%2FM909vccoWic74rBWAMJuEXbY7qKqMcUJQt4d7U8FaVIofb1iPlkoOvXmpRJRpfKsXy0OM62ZvdDoKOscIvBXr6y5QAursKXmZkJus1AV6%2Fw%2FbD%2FoDkLGrxvYzY7alc3aVrxMYzcwxvBAWzIcMvovuxIl%2FQ8oTrmlUSOVA3RK93xGoABgSZSgv9GieOwVAhZcBP%2Ff6NCPBIJkOXSUDRUiIqoLG0NMAEvGz1kHRhxkSShhCrHGqFD1OXkwdmwzOtcE8s%2F3VP6%2Fw4t6kj0pFtSkl7HWbvyI1Pdxd%2Fs6GLV8xnoIoSQAAOTNjIHUHVx22GPGGDGmMcsAphusXkjHmB5KAldSL0gAA%3D%3D&OSSAccessKeyId=STS.NUUne5bNvJvNEWSyotKQANuNq&Expires=1728390048&Signature=AWhsgR2D3xRMFZZ35PKpUVPwjH4%3D -pix_fmt rgb24 /tmp/screen.record.gif 2024-10-08T11:21:01.793Z 1-6705158b-15aae364-e8b091****** [INFO] Uploaded /tmp/screen.record.gif to output/screen.record.gif 2024-10-08T11:21:01.796Z 1-6705158b-15aae364-e8b091****** [INFO] current Function [handler] excute time is 13.32 seconds FC Invoke End RequestId: 1-6705158b-15aae364-e8b091****** Duration: 13803.77 ms, Billed Duration: 13804 ms, Memory Size: 1024 MB, Max Memory Used: 414.34 MB ========= FC invoke Logs end ========= Invoke instanceId: c-6705158b-152fc2e0-5ca045****** Code Checksum: 5414709321074418652 Qualifier: LATEST RequestId: 1-6705158b-15aae364-e8b091****** Invoke Result: ok [VideoGif] completed (18.86s)
  ```

## **相关文档**

- 如果您需要加快大视频的转码速度或者完成多种复杂的组合操作，可以通过Serverless工作流编排函数实现视频处理系统，具体请参见[构建基于Serverless架构的弹性高可用音视频处理系统](https://help.aliyun.com/zh/functioncompute/fc/use-cases/build-an-elastic-and-highly-available-audio-and-video-processing-system-in-a-serverless-architecture)。
- 如果您需要实时或者准实时的音视频处理，可以使用GPU实例部署对应的应用，具体请参见[音视频处理最佳实践](https://help.aliyun.com/zh/functioncompute/best-practices-for-audio-and-video-processing-1)。
