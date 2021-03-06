使用说明: 如何针对具有相同登录信息(如 用户名, 端口, 登录秘钥)的主机, 以组(以下称为主机组)为单位批量进行磁盘IO性能测试

脚本的环境需求:
   脚本运行需要发起测试的主机拥有被测试机器的免密登录权限.
   被测主机最好具有相同或相似规格的磁盘设备,被批量测试的主机通用配置,如,内存,CPU,网络设备等,尽量不要有太大幅度差异,
   尽量保证所有主机的连接不会受网络影响产生连接中断,默认情况下脚本的预检测和fio测试途中都会对网络进行测试,若主机连接因网络中断则脚本可能会终止并报错,
   手动测试情况下(不同于通用测试步骤)如果对于网络质量不能保证请使用'-f'选项保证测试跳过中间错误的部分和忽略失联的主机继续进行.

##############################################################################################################################################
#       通用测试步骤
##############################################################################################################################################

    以下测试操作动作均在跳板机上完成:

    1). 将主机组的登录信息添加到配置文件 'cfiojobs.grp'

        格式如下:
        组名             用户名  端口      --          --          主机IP或主机名列表文件路径
        host_group_name  root    22        --          --          -/root/hostname_list_file

        注意:主机名的列表文件路径以 '-' 开头, 请尽量使用绝对路径表示文件的位置, 
             主机名或IP列表格式为, 每一行一个IP地址或主机名, 若某一行主机名或IP地址以'#'开头, 则该行信息被剔除.

        另外(通常你应该不会用到),
            在 'cfiojobs.grp' 中的 '主机IP或主机名列表文件路径' 字段, 你可以直接填写 要登录的主机IP或者主机名, 多个IP/主机名之间使用逗号分割,相互不要有空格, 同样可以生效.
            如果在 'conf/' 目录下 以 '<组名>.grp' 存储 主机名或IP列表时, 可以将主机列表的文件路径简写为 '--', 'conf/<组名>.grp'是默认的主机列表信息读取位置.

    2). 执行测试检查

        请运行命令:
            './group.sh'

        检查内容包含:

        01. 配置信息,网络可达性,免密登录状态,fio软件包等
            该命令运行环境检查时会针对检测到的异常直接给出报错提示,如有异常,请根据提示先排查解决环境配置具体问题,清空'grouplist'文件,然后重新运行无报错后再继续.

            注, 如果要强行忽略报错的组继续测试, 请直接编辑'grouplist'文件,将报错的组名强制加进去即可进行下一步.

        02. 磁盘设备配置检查 (该步骤将需要你结合自身可用的设备资产状况手动完成核对,请耐心完成!)

            脚本会自动统计生成集群中未被使用的裸设备列表,会为进行测试的每一组主机在 'conf/' 目录下生成名为 '<组名>.blk' 的设备列表文件.
            针对该组的测试将基于此列表进行执行(不存在的设备会被忽略),你可以对生成的信息进行检查,并针对自身的设备配置进行调整.

            因为测试环境的设备配置千差万别,各自的规格和用途规划无法进行统一,所以请仔细核对将非测试用途的设备剔除,然后在进行下一步.

        03. 如无异常,测试检查结果会在最后一行给出开始测试执行的具体命令.

    3). 开始测试

        第 2) 步 中 'group.sh' 脚本的最后一行内容输出为执行 并行/单盘 对比测试的具体命令,复制最后一行命令文本粘贴到终端运行即可开始测试.

        默认测试将包含 并行磁盘测试和单盘磁盘测试, 测试完成将自动对比两次结果差异并在脚本目录内生成excel格式的测试表格.

        快速查看被测主机上的作业状态可以使用命令
            './cfiojobs -l'

        更详细的进度信息可以在 名为 '<组名><模式><时间>.log' 的日志文件中查看. 

##############################################################################################################################################
#       故障排查与调整配置:
##############################################################################################################################################

    1). 运行环境检查

	    -1). 统一检查, 请运行以下命令:
	        './cfiojobs -afc'

        说明: './cfiojobs' 为测试主程序脚本, '-a' 代表所有组, '-f'代表尽可能跳过(如部分主机失联,集群磁盘数量不一致等)错误使测试完成, '-c'代表进行检查(包含fio和磁盘配置比对)

        -2). 单独检查某一组, 使用命令:
	        './cfiojobs -g <组名> -fc' 

        说明: 被检查组的可测试磁盘列表将自动保存在 'conf/<组名>.blk' 文件中, 如果该文件已存在则不会再自动生成.
              将检查正常的组名会被自动添加到'grouplist'文件中, 每行一个, 测试开始之前, 可使用'#'注释舍弃的测试组


    2). 测试的具体执行程序为 fio, fio的参数也将以组的形式 被预定义在 'cfiojobs.job' 文件中,你也可以检查并修改其中需要调整的参数,
        默认情况下测试会使用的作业组名为 'normal', 你可以在 './lib/global_profile' 中找到对应的配置项并修改它.

    3). 所有的命令分发都使用ssh完成, 最大并发连接主机数为500, ssh的超时时间默认为15秒, 你也可以在 './lib/global_profile' 中找到配置项并修改.

    4). 主脚本 'cfiojobs' 提供了文件分发收集, 命令/脚本批量执行, 输出对比统计, 单轮测试重测/测试恢复等额外功能, 使用 './cfiojobs -h' 可以获得参数说明.
        在 'bin/' 目录下,
            'cfiojobs.json.py' 提供了fio的json日志的基本检查功能,
            'cfiojobs.log2.py' 提供了 并行/单盘 模式日志目录内容的重新分析功能,
            'cfiojobs.contrast2.sh' 提供了 并行与单盘测试结果对比 并生成excel的功能.
            另外:
            'cfiojobs.scatter.py' 提供了 多次 rbd块性能测试 的结果对比 生成excel报告的功能.

        每一个脚本均包含帮助信息, 不加参数直接运行即可获取对应的帮助信息.

    5). 混合任务执行(如果你不了解Linux脚本, 也不清楚每个参数到底干了什么,请你不要使用这个功能)

        主脚本 'cfiojobs' 并不限制多种任务,多个主机组和多个测试作业,以及多个磁盘组同时被指定,
        但是同一次指定的多个测试参数, 冲突的部分(因为涉及测试的部分会有设备抢占)会被逐级先后分开再先后执行,
        它们的结果信息会被按组(顺序为:磁盘组,作业组,主机组)分别统计到各自的报告目录中, 各自独立存放.

        一般情况下不建议 将复杂的 批量命令, 批量脚本, 文件分发收集与磁盘测试任务同时执行, 但是它们的参数的确可以被手动指定组合在一起工作.
        当 文件分发,命令/脚本批量执行, 磁盘fio作业 同时发起时, 三者都会被主机组批量执行, 但是在具体的某一台主机上, 它们依然是顺序的, 默认顺序为:
            1).拷贝文件到主机,
            2).运行fio作业,
            3).执行给定的命令,
        使用'-A'选项时,可调转2和3的顺序,即先执行给定的命令后运行测试.
        默认当命令与fio测试一起执行时,命令仅执行一次,使用'-E'选项可以使命令在每一轮测试都执行

    6). 如过还需获取更加细致的参数帮助,请运行:
        './cfiojobs -h'
        并仔细阅读帮助信息,其中可能有困惑的部分已经在本文下一段落的 其他使用说明 部分进行了进一步说明.

##############################################################################################################################################
#       其他使用说明:
##############################################################################################################################################

1. 运行测试的多个主机为一组,
        配置文件:
        cfiojobs.grp
   主机组的使用方式与clustershell基本保持一致
   配置文件格式:
     第一列,主机组的名称,名称需要唯一不重复,
     第二列,主机组内主机的ssh登录用户,在多个可登陆用户中指定其一
     第三列,主机组内主机的ssh登录端口
     第四列,该主机组对应的后端服务器,使用逗号分隔后端服务器的登录信息,即:"用户,端口,ip",若无,填写'none'
     第五列,该主机对应的后端服务器2,格式同第四列
     第六列,主机组内的主机IP地址列表,多个ip使用逗号分隔,中间可以换行,每一行的逗号后可以包含以'#'开头的注释,以便标注不同的主机信息
            可以在结尾使用'--'表示使用单独的文件存储ip列表,
            将跟组名相同的以'.grp'结尾的配置文件存放到'conf/'目录即可,
            额外的ip列表文件每行一个ip地址,可以使用'#'开头作为注释,不需要使用逗号分隔.
     其中,字段之间可以使用空格或者tab制表符作为间隔和缩进,字段信息不使用引号
   使用方式: 
     使用'-g <组名>'   调用文件中指定的组执行任务,
     使用'-x <ip地址>' 剔除特定的主机,
     使用'-a'          在所有组运行任务,
     使用'-X <组名>'   剔除指定的组.


2. 测试的包含一定参数范围(如4k,256k,4m多个块大小)的作业为一个作业组,
        配置文件:
        cfiojobs.job
   其中,名为'DEFAULT'的组其作业的fio选项及参数可以被其他组继承
   配置文件格式:
     第一列,作业组的名称,名称唯一.
     第二列,该组作业运行时长,runtime, 
            该列必须为数字,
            或者'none'表示不指定
     第三列,该组作业测试数据量大小,size, 
            该列必须为指定的容量信息,可以是指定的大小值,如'100G',或者百分比值,如'100%',
            或者'random'表示使用1%-100%的随机值.
            该列不能留空,否则fio不能正常测试
     第四列,该组作业的块大小列表,bs,多个块值使用逗号分隔,
            该列必须为块大小字符串.如'4k,256k',
            或者"none",表示不指定,
            如果,使用混合读写模式特定比例的块大小测试,
                bs设置为'none',然后将'bssplit'参数写在自定义选项参数中即可.
     第五列,是否将缺省选项和参数从DEFAULT组中继承,
            若DEFAULT组包含10个选项及相关参数,当前组只需要调整其中一个选项来作为新的一组,
            则此处填写'True',再在下一个fio的选项和参数字段部分,仅填写需要调整的那一个和'DEFAULT'不同的选项和对应参数即可.
     第六列,fio作业的所有其他测试选项和参数,因为参数通常会很多,这里有两种选项分隔方式:
            -1.使用逗号分隔多个选项,选项和参数之间不使用空格
            -2.使用双引号,并在内部使用空格分隔,选项和参数之间不使用空格
     注意,使用模板示例的选项将自动生成对应的测试报告,
            增加fio的作业选项自动生成的报告将不会进行统计,
            如果减少作业的选项将可能影响自动生成报告的结果.
   使用方式:
     使用'-j  <作业组名>' 即可调用该组参数执行任务,多个作业组名使用逗号分隔


3. 测试的多个磁盘或者文件为一个磁盘组,
        配置文件:
        cfiojobs.blk
   其中,指定名称的磁盘必须在测试主机上统一存在,如果指定的是文件,当其不存在时fio会自动创建该文件.
   配置文件格式一:
     第一列,磁盘组名称,名称唯一 
     第二列,磁盘/文件列表的绝对路径列表,多个磁盘或者文件之间使用逗号分隔,中间可以换行,每一行后可以使用'#'开头的注释以便标注信息.
   配置文件格式二:
       如果需要测试的对象较多,如进行数百个rbd的测试,可以使用单独的配置文件,将其存放在'conf/'目录中,文件名以'.blk'结尾即可
       每行填写一个测试块对象名称,请填写完整路径,如,'/dev/sdc',
       如果rbd指定'pool'选项已经指定,则可以仅填写rbd名称,如'img001'
   使用方式:
     使用'-b  <磁盘组名>'  即可调用填写好的组信息运行测试

4. 脚本的配置文件不存在时使用'-e'可以生成简单的参考样本

5. 更多fio测试选项
     --fio          发起fio测试
     --fio-list     显示fio作业在各个主机的运行状态列表
     --fio-stop     跳过某一组主机正在运行的fio作业
     --test-stop    停止某一组测试
     --round-list   给出测试将发起的每一轮测试的编号和模式信息
     --round-retest 针对指定的某一轮或某几轮测试进行重测.
     --recover      如果测试意外停止,可以使用该选项恢复中断的测试
     --recover-from 从给定的某一轮开始继续测试
     -b             指定作业的磁盘组
     -j             指定作业的作业组
     -A             运行作业时先执行给定的命令
     -o             指定输出文件夹(不指定则使用时间戳)
     -s             单盘模式,fio作业一次仅一个磁盘
     -c             对测试环境进行与检查
   示例:
         ./cfiojobs -g group1 --fio-list
         ./cfiojobs -g group1 --fio-stop
         ./cfiojobs -g group1 --fio -b blkgroup1 -j job1 -A 'dd if=/dev/zero of=/dev/sdb bs=4M count=12800' -F file1,file2,file3 -D /tmp -o test0808
   提示: 
         ./cfiojobs -g <组名> ls -pqf
         可以进行快速的网络环境检查, 这里是使用了批量执行'ls'命令并检查返回值观察结果的方式完成的,仅作为示范.
         ./cfiojobs -g <组名> -fc 
         可以进行有效的环境检查,并给出可测试的裸盘列表,请养成良好的检查习惯.

6. 脚本的其他选项
     -e            生成配置文件模板
     -t            运行之前执行检查主机组配置文件
     -q            减少运行信息输出,仅给出当前进度的标题信息和执行结果返回值
     -d            显示函数接收到的参数与运行状态,并尝试跳过失败的部分继续运行
     -f            尝试跳过失败的部分继续运行脚本
     -p            发送命令与拷贝文件的动作都会被放到后台并行执行,
                   注意,'-p' 仅在未发起fio测试作业的前提下生效,
                   fio测试时默认将以并行方式运行,该选项无意义.
                   并行模式的返回结果以各自在后台的结束时间为顺序,不会顺次返回标准输出.
     -F            指定需要分发的文件,多个文件使用逗号分隔
     -C            指定需要收集的文件,多个文件使用逗号分隔,使用该参数请指定输出文件夹.
     -D            指定分发文件到目标主机上的位置(如果未指定,默认使用用户家目录)
     --script      在主机组上批量运行指定的脚本
     --argument    为批量运行的脚本传递参数
     -h            显示帮助信息
     -v            显示版本信息

7. 其他命令示例与说明
   执行简单命令: 
     如, 批量执行 lsblk 到 group1组:
         ./cfiojobs -g group1 lsblk:
   关于shell的远程命令的引号使用:
     命令包含远端主机的环境变量,需要使用单引号,从而保证命令不被转译,如
         ./cfiojobs -g group3 'ls /var/lib/ceph/mon/ceph-$HOSTNAME/'
     命令使用当前主机shell变量或者管道,如
         ./cfiojobs -g group2 "ps aux |grep mysql"
         ./cfiojobs -g group4 "yum -y install $pkg_name"
     命令使用awk等包含内部变量的程序命令,需要使用单引号加反引号,如
         ./cfiojobs -g group5 "ls -l |awk '{print\$2}'"
    如果执行的命令较为复杂建议编写单独的shell脚本,并使用'--script' 选项批量执行.

8. 各个测试脚本功能说明
   1).快速批量测试脚本 
        './group.sh'
      脚本会针对'grouplist'文件中的组自动完成指定的测试,
      默认输出目录'<组名><模式><日期>'
      默认输出日志'<组名><模式><日期>.log'
      并在测试完成后会自动生成测试的Excel格式信息表格,
   2).json文件检查脚本
        './bin/cfiojobs.json.py'
        仅检查json日志能否正常读取
   3).日志分析脚本 
        './bin/cfiojobs.log2.py'
      可以自动生成一次测试或者一台主机测试的输出目录下日志的分析结果,报告使用csv格式表格.
      完整集群测试报告,
        不需要任何参数,该脚本加测试输出目录即可,结果输出到测试目录下的'_report'目录(可在Excel打开).
      仅针对测试中的某一台主机单独生成报告,请使用'nocompare'参数完成
        './bin/cfiojobs.log2.py  <主机日志目录>  nocompare'
        结果同样在'_report'子目录中,该报告仅为linux下快速查看某一主机测试结果,使用'utf-8'编码不能在Excel直接打开.
      若针对rbd测试生成rbd模式的报告,请使用'rbd'参数
        './bin/cfiojobs.log2.py  <主机日志目录>  rbd'
        该模式结果将包含延迟分布信息
   4).测试报告对比结果汇总脚本
        './bin/cfiojobs.log2.sh'
        该见脚本被'group.sh'调用,可以自动对比两次测试的磁盘报告并生成excel汇总表格,如果需要重新生存报告可以手动运行该脚本,
        请注意,如果指定的输出excel文件已经存在,该脚本并不会覆盖而是将新的报告追加到原有报告尾部,如果不想报告重合请指定新的文件名
   5).csv查看脚本 
        './bin/catcsv.sh'
      使用"./catcsv.sh csv文件名" 即可在shell窗口中获得该文件的快速预览结果.(仅支持utf8编码).
   6).针对rbd性能对比测试报告,自动生成excel散点图图表脚本 
        './bin/cfiojobs.scatter.py'
        配置文件 './bin/cfiojobs.scatter.py.ini'
        其中,配置文件的列编号使用从1开始的自然数
      该脚本可以在配置文件中自定义调整:
        测试模式信息所在的列, key_column_num
        需要对比指标的数据列, data_columns
        延迟分布信息的数据列, surface_columns_range
   7).测试中关联运行外部shell脚本.
      可以指定任意主机组在测试中一起运行指定的外部shell脚本,
      在'conf'目录下'<组名>.bsh'文件中将需要批量执行的外部脚本名称填好即可,
      如果需要测试中的信息传递给外部的脚本,可修改在脚本的'_record_backend'函数中,根据需求添加信息到'bknd_sh_pass_in'变量中即可.

