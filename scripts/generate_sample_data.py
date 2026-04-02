import os
import sys
import scanpy as sc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_utils import init_logger

logger = init_logger()


def generate_pbmc3k_sample(output_dir="sample_data"):
    """
    生成PBMC3k示例数据
    
    Args:
        output_dir: 输出目录
    """
    logger.info("开始生成PBMC3k示例数据...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        adata = sc.datasets.pbmc3k_processed()
        output_path = os.path.join(output_dir, "pbmc3k.h5ad")
        adata.write(output_path)
        logger.info(f"✅ PBMC3k示例数据已保存至: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ 生成PBMC3k示例数据失败: {e}")
        raise


def generate_10x_mtx_sample(output_dir="sample_data"):
    """
    生成10x格式示例数据（简化版）
    
    Args:
        output_dir: 输出目录
    """
    logger.info("开始生成10x格式示例数据...")
    
    mtx_dir = os.path.join(output_dir, "10x_sample")
    os.makedirs(mtx_dir, exist_ok=True)
    
    try:
        adata = sc.datasets.pbmc3k()
        
        import scipy.io
        import gzip
        import pandas as pd
        
        scipy.io.mmwrite(os.path.join(mtx_dir, "matrix.mtx"), adata.X.T)
        with open(os.path.join(mtx_dir, "barcodes.tsv"), 'w') as f:
            for bc in adata.obs_names:
                f.write(bc + '\n')
        
        features = pd.DataFrame({
            'gene_id': adata.var_names,
            'gene_name': adata.var_names,
            'feature_type': 'Gene Expression'
        })
        features.to_csv(os.path.join(mtx_dir, "features.tsv"), sep='\t', header=False, index=False)
        
        for ext in ['.mtx', '.tsv', '.tsv']:
            src = os.path.join(mtx_dir, ["matrix", "barcodes", "features"][[".mtx", ".tsv", ".tsv"].index(ext)] + ext)
            with open(src, 'rb') as f_in:
                with gzip.open(src + '.gz', 'wb') as f_out:
                    f_out.writelines(f_in)
            os.remove(src)
        
        logger.info(f"✅ 10x格式示例数据已保存至: {mtx_dir}")
        return mtx_dir
    except Exception as e:
        logger.error(f"❌ 生成10x格式示例数据失败: {e}")
        raise


if __name__ == "__main__":
    print("=" * 80)
    print("LocalSingleCell 示例数据生成工具")
    print("=" * 80)
    print()
    
    try:
        pbmc_path = generate_pbmc3k_sample()
        print()
        print("=" * 80)
        print("✅ 所有示例数据生成完成！")
        print(f"   - PBMC3k处理后数据: {pbmc_path}")
        print("=" * 80)
    except Exception as e:
        print(f"❌ 示例数据生成失败: {e}")
        sys.exit(1)
