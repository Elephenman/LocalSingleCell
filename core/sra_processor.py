import os
import subprocess
import tempfile
import shutil
from core import data_loader


def check_tool_installed(tool_name):
    """
    检查工具是否安装
    
    Args:
        tool_name: 工具名称
    
    Returns:
        bool: 是否已安装
    """
    try:
        subprocess.run(
            [tool_name, '--version'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def download_sra(sra_id, output_dir):
    """
    下载SRA文件
    
    Args:
        sra_id: SRA编号
        output_dir: 输出目录
    
    Returns:
        str: 下载的SRA文件路径
    """
    try:
        # 使用prefetch下载SRA文件
        subprocess.run(
            ['prefetch', sra_id, '-O', output_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 返回SRA文件路径
        sra_file = os.path.join(output_dir, f'{sra_id}.sra')
        if os.path.exists(sra_file):
            return sra_file
        else:
            # 可能在子目录中
            sra_file = os.path.join(output_dir, sra_id, f'{sra_id}.sra')
            if os.path.exists(sra_file):
                return sra_file
            else:
                raise Exception(f"无法找到下载的SRA文件: {sra_id}")
    except Exception as e:
        raise Exception(f"下载SRA文件失败: {str(e)}")


def convert_sra_to_fastq(sra_file, output_dir):
    """
    将SRA文件转换为fastq文件
    
    Args:
        sra_file: SRA文件路径
        output_dir: 输出目录
    
    Returns:
        list: fastq文件路径列表
    """
    try:
        # 使用fasterq-dump转换SRA文件
        subprocess.run(
            ['fasterq-dump', sra_file, '-O', output_dir, '--split-files'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 查找生成的fastq文件
        fastq_files = []
        for file in os.listdir(output_dir):
            if file.endswith('.fastq'):
                fastq_files.append(os.path.join(output_dir, file))
        
        if not fastq_files:
            raise Exception("转换SRA文件失败，未生成fastq文件")
        
        return fastq_files
    except Exception as e:
        raise Exception(f"转换SRA文件失败: {str(e)}")


def run_starsolo(fastq_files, genome_index, output_dir):
    """
    使用STARsolo进行定量
    
    Args:
        fastq_files: fastq文件路径列表
        genome_index: 基因组索引路径
        output_dir: 输出目录
    
    Returns:
        str: 定量结果目录路径
    """
    try:
        # 构建STARsolo命令
        cmd = [
            'STAR',
            '--runMode', 'alignReads',
            '--genomeDir', genome_index,
            '--readFilesIn', *fastq_files,
            '--readFilesCommand', 'zcat' if any(f.endswith('.gz') for f in fastq_files) else '',
            '--outFileNamePrefix', os.path.join(output_dir, ''),
            '--outSAMtype', 'BAM', 'Unsorted',
            '--soloType', 'CB_UMI_Simple',
            '--soloCBwhitelist', 'None',
            '--soloUMIlen', '10',
            '--soloCBlen', '16',
            '--soloFeatures', 'Gene'
        ]
        
        # 执行STARsolo命令
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 返回定量结果目录
        solo_out_dir = os.path.join(output_dir, 'Solo.out', 'Gene', 'filtered')
        if os.path.exists(solo_out_dir):
            return solo_out_dir
        else:
            raise Exception("STARsolo定量失败，未生成结果目录")
    except Exception as e:
        raise Exception(f"STARsolo定量失败: {str(e)}")


def process_sra(sra_id, temp_dir, genome_index=None):
    """
    处理SRA数据的完整流程
    
    Args:
        sra_id: SRA编号
        temp_dir: 临时目录
        genome_index: 基因组索引路径（可选）
    
    Returns:
        AnnData对象
    """
    try:
        # 检查工具是否安装
        if not check_tool_installed('prefetch'):
            raise Exception("未安装SRA Toolkit，请先安装")
        
        if not check_tool_installed('fasterq-dump'):
            raise Exception("未安装SRA Toolkit，请先安装")
        
        if not check_tool_installed('STAR'):
            raise Exception("未安装STAR，请先安装")
        
        # 如果没有提供基因组索引，使用默认索引（这里需要根据实际情况修改）
        if genome_index is None:
            # 这里应该使用用户提供的基因组索引或下载默认索引
            raise Exception("请提供基因组索引路径")
        
        # 下载SRA文件
        sra_file = download_sra(sra_id, temp_dir)
        
        # 转换为fastq文件
        fastq_files = convert_sra_to_fastq(sra_file, temp_dir)
        
        # 使用STARsolo进行定量
        quant_dir = run_starsolo(fastq_files, genome_index, temp_dir)
        
        # 读取定量结果
        adata = data_loader.read_10x_mtx(quant_dir)
        
        return adata
    except Exception as e:
        raise Exception(f"处理SRA数据失败: {str(e)}")