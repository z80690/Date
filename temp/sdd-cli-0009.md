
# SDD
SDD（Specification-Driven Development）是一种规格驱动开发模式，严格通过"需求规格、技术设计、任务规划、编码实现"四个阶段推进工作。这种结构化流程旨在保障每一步开发均有据可依，实现过程可控与历史可查。
#### SDD命令概述表
表1SDD命令概述表 
| 命令          | 输入说明                                                                                                                                                                                                      | 输出产物路径                                            | 功能说明                                         |
|:---|:---|:---|:---|
| /sdd-new    | /sdd-new + *需求描述*，必选参数                                                                                                                                                                                    | *{项目根路径}* /.codeartsdoer/specs/*产物文件夹名*/spec.md   | 根据需求描述生成spec.md文档，即定义"做什么"，如业务行为、需求约束等。      |
| /sdd-design | /sdd-design + *产物文件夹名，*可选参数，系统会从对话上下文自动推断上一阶段的产物文件夹名 注意： 必须存在目录（*{项目根路径}* /.codeartsdoer/specs/*产物文件夹名*）和生成的spec.md。 | *{项目根路径}* /.codeartsdoer/specs/*产物文件夹名*/design.md | 基于spec.md生成design.md文档，即定义"怎么做"，如技术架构、实现方案等。 |
| /sdd-tasks  | /sdd-tasks + *产物文件夹名，*可选参数，系统会从对话上下文自动推断上一阶段的产物文件夹名 注意： 必须同时存在spec.md和design.md。                                         | *{项目根路径}* /.codeartsdoer/specs/*产物文件夹名*/tasks.md  | 基于spec.md和design.md生成任务清单tasks.md            |
| /sdd-apply  | /sdd-apply + *产物文件夹名* ，可选参数，系统会从对话上下文自动推断上一阶段的产物文件夹名，**直接在主智能体中执行** 注意： 必须同时存在spec.md、design.md和tasks.md。               | 代码 + 更新tasks                                      | 按tasks.md逐项执行编码任务                            |
   
![](https://support.huaweicloud.com/usermanual-cli/public_sys-resources/note_3.0-zh-cn.png)
*产物文件夹名* 由模型自主生成。受生成随机性影响，即使输入相同的需求描述，输出的*产物文件夹名*也可能存在差异。
#### 使用SDD生成代码
1. 进入TUI开发环境。 
   1. 打开目标项目的根目录。
   
   2. 鼠标右键单击空白处，选择"在终端中打开"。
   
   3. 在终端中输入"codearts"并回车，即可进入TUI开发环境。
   
   
   
   
2. **创建需求规格** 。在TUI对话框中，输入"/sdd-new *需求描述* "并回车，生成spec.md文件。
   
   图1创建需求规格   
   ![](https://support.huaweicloud.com/usermanual-cli/zh-cn_image_0000002629431980.png "点击放大")
   需求规格创建完成后，进入*{项目根路径}* /.codeartsdoer/specs/*产物文件名*目录下，可查看到生成的spec.md。如果生成的spec.md不符合您的预期，可以通过手动或智能体进行修改。
   
   
3. **创建技术设计** 。在TUI对话框中，输入"/sdd-design"并回车，基于spec.md生成design.md文档。
   
   图2创建技术设计   
   ![](https://support.huaweicloud.com/usermanual-cli/zh-cn_image_0000002659759767.png "点击放大")
   技术文档设计完成后，进入*{项目根路径}* /.codeartsdoer/specs/*产物文件名*目录下，可查看到生成的design.md。如果生成的design.md不符合您的预期，可以通过手动或智能体进行修改。
   
   
4. **创建编码任务** 。在TUI对话框中，输入"/sdd-tasks"并回车，基于spec.md和design.md生成任务清单tasks.md。
   
   图3生成编码任务   
   ![](https://support.huaweicloud.com/usermanual-cli/zh-cn_image_0000002629287454.png "点击放大")
   编码任务规划文档设计完成后，进入*{项目根路径}* /.codeartsdoer/specs/*产物文件名*目录下，可查看到生成的tasks.md。如果生成的tasks.md不符合您的预期，可以通过手动或智能体进行修改。
   
   
5. **执行编码实现** 。在TUI对话框中，输入"/sdd-apply"并回车，智能体会按tasks.md逐项执行编码任务。
   
   图4执行编码任务   
   ![](https://support.huaweicloud.com/usermanual-cli/zh-cn_image_0000002629289478.png "点击放大")
   
   
 
