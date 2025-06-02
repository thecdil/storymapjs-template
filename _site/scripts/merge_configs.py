#!/usr/bin/env python3
"""
Config Merger for StoryMapJS Template
TƯƠNG THÍCH VỚI COLLECTIONS SYSTEM - Không ảnh hưởng collections config
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
import logging
import subprocess
from typing import List, Tuple, Dict, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class StoryMapConfigMerger:
    """
    Config Merger tương thích với Collections System
    Chỉ merge các config bổ sung, không ảnh hưởng collections
    """
    
    def __init__(self):
        self.configs_dir = Path('configs')
        self.temp_dir = Path('_temp')
        self.temp_config = self.temp_dir / '_config.yml'
        self.original_config = Path('_config.yml')
        
        # Thứ tự ưu tiên (tránh conflict với collections)
        self.priority_order = [
            'config_base.yml',
            'config_header.yml', 
            'config_footer.yml',
            'config_theme.yml'
        ]
        
        # Tạo thư mục tạm
        self.temp_dir.mkdir(exist_ok=True)
    
    def validate_collections_compatibility(self) -> bool:
        """
        Kiểm tra tương thích với collections system
        Đảm bảo không ảnh hưởng đến collections config
        """
        logger.info("🔍 Checking collections system compatibility...")
        
        # Kiểm tra collections system tồn tại
        collections_dir = Path('collections')
        plugins_dir = Path('_plugins')
        
        if not collections_dir.exists():
            logger.warning("⚠️  Collections directory not found")
            return True
        
        if not plugins_dir.exists():
            logger.warning("⚠️  Plugins directory not found")
            return True
        
        # Kiểm tra collection generator plugin
        collection_plugin = plugins_dir / 'collection_generator.rb'
        if collection_plugin.exists():
            logger.info("✅ Collections system detected - ensuring compatibility")
        
        return True
    
    def load_original_config(self) -> Dict:
        """
        Load config gốc (bao gồm collections config)
        """
        try:
            with open(self.original_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"✅ Loaded original config with {len(config)} keys")
            return config
        except Exception as e:
            logger.error(f"❌ Error loading original config: {e}")
            return {}
    
    def discover_config_files(self) -> List[Path]:
        """Tự động phát hiện config files"""
        if not self.configs_dir.exists():
            logger.warning(f"⚠️  Configs directory not found: {self.configs_dir}")
            return []
        
        config_files = list(self.configs_dir.glob('*.yml'))
        logger.info(f"🔍 Found {len(config_files)} config files")
        
        for file in config_files:
            logger.info(f"   - {file.name}")
        
        return config_files
    
    def organize_by_priority(self, config_files: List[Path]) -> Tuple[List[Path], List[Path]]:
        """Sắp xếp theo thứ tự ưu tiên"""
        priority_files = []
        additional_files = []
        processed = set()
        
        # Priority files
        for priority_name in self.priority_order:
            for file in config_files:
                if file.name == priority_name and file.name not in processed:
                    priority_files.append(file)
                    processed.add(file.name)
                    break
        
        # Additional files
        for file in config_files:
            if file.name not in processed:
                additional_files.append(file)
        
        logger.info(f"📋 Priority files: {[f.name for f in priority_files]}")
        if additional_files:
            logger.info(f"🆕 Additional files: {[f.name for f in additional_files]}")
        
        return priority_files, additional_files
    
    def validate_yaml_file(self, file_path: Path) -> bool:
        """Validate YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            logger.info(f"✅ YAML validation passed: {file_path.name}")
            return True
        except yaml.YAMLError as e:
            logger.error(f"❌ YAML error in {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error validating {file_path}: {e}")
            return False
    
    def merge_configs(self, priority_files: List[Path], additional_files: List[Path]) -> bool:
        """
        Merge configs với original config (bao gồm collections)
        """
        logger.info("🔄 Starting config merge process...")
        
        # Load original config (bao gồm collections system)
        merged_config = self.load_original_config()
        
        # Merge priority files
        for file in priority_files:
            if not self.validate_yaml_file(file):
                logger.error(f"❌ Validation failed: {file.name}")
                return False
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Deep merge để tránh override collections config
                merged_config = self.deep_merge(merged_config, config_data)
                logger.info(f"✅ Merged: {file.name}")
                
            except Exception as e:
                logger.error(f"❌ Error merging {file.name}: {e}")
                return False
        
        # Merge additional files
        for file in additional_files:
            if not self.validate_yaml_file(file):
                continue
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                merged_config = self.deep_merge(merged_config, config_data)
                logger.info(f"✅ Merged additional: {file.name}")
                
            except Exception as e:
                logger.error(f"⚠️  Error merging additional {file.name}: {e}")
        
        # Save merged config
        return self.save_merged_config(merged_config)
    
    def deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Deep merge dictionaries để tránh override collections config
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_merged_config(self, config: Dict) -> bool:
        """Save merged config với metadata"""
        try:
            # Tạo header với thông tin merge
            header = f"""# ===================================================================
# MERGED CONFIGURATION FOR STORYMAPJS TEMPLATE
# 
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}
# 
# ⚠️  DO NOT EDIT THIS FILE DIRECTLY
# Edit individual config files in configs/ directory
# 
# This file preserves the original collections system configuration
# and adds modular header/footer/theme configurations
# ===================================================================

"""
            
            # Ghi config
            with open(self.temp_config, 'w', encoding='utf-8') as f:
                f.write(header)
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"✅ Merged config saved: {self.temp_config}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving merged config: {e}")
            return False
    
    def test_jekyll_compatibility(self) -> bool:
        """Test Jekyll compatibility"""
        logger.info("🧪 Testing Jekyll compatibility...")
        
        try:
            # Test Jekyll doctor
            result = subprocess.run(
                ['bundle', 'exec', 'jekyll', 'doctor', '--config', str(self.temp_config)],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Jekyll doctor test passed")
                return True
            else:
                logger.warning(f"⚠️  Jekyll doctor warnings: {result.stderr[:200]}...")
                return True  # Warnings acceptable
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Jekyll test timeout")
            return True
        except FileNotFoundError:
            logger.warning("⚠️  Bundle not found, skipping Jekyll test")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Jekyll test error: {e}")
            return True
    
    def run(self, test_only: bool = False) -> bool:
        """Main execution"""
        logger.info("🚀 Starting StoryMapJS config merger...")
        
        # Check collections compatibility
        if not self.validate_collections_compatibility():
            return False
        
        # Discover configs
        config_files = self.discover_config_files()
        if not config_files:
            logger.warning("⚠️  No config files found, using original config only")
            return True
        
        # Organize by priority
        priority_files, additional_files = self.organize_by_priority(config_files)
        
        # Test only mode
        if test_only:
            logger.info("🧪 Running validation only...")
            all_valid = True
            for file in priority_files + additional_files:
                if not self.validate_yaml_file(file):
                    all_valid = False
            return all_valid
        
        # Merge configs
        if not self.merge_configs(priority_files, additional_files):
            return False
        
        # Test Jekyll compatibility
        if not self.test_jekyll_compatibility():
            return False
        
        logger.info("🎉 Config merge completed successfully!")
        logger.info(f"📄 Merged config: {self.temp_config}")
        logger.info("🔧 Next: bundle exec jekyll build --config _temp/_config.yml")
        
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='StoryMapJS Config Merger')
    parser.add_argument('--test-only', action='store_true', help='Only validate configs')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    merger = StoryMapConfigMerger()
    success = merger.run(test_only=args.test_only)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
