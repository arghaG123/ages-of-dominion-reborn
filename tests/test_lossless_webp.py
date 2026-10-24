from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys
import shutil
import uuid
import unittest
from PIL import Image, ImageCms

ENCODER = Path(__file__).resolve().parents[1] / 'scripts/build-lossless-webp.py'
SCRATCH = ENCODER.parents[1] / 'scratch'

@contextmanager
def workspace_directory():
    # Windows' private tempfile ACL omits the restricted process SID. Use the
    # explicitly writable workspace, and verify the exact scope before cleanup.
    directory = SCRATCH / ('webp-unit-' + uuid.uuid4().hex)
    directory.mkdir(mode=0o777)
    try:
        yield directory
    finally:
        assert directory.resolve().parent == SCRATCH.resolve()
        assert directory.name.startswith('webp-unit-')
        shutil.rmtree(directory)

class LosslessWebpTests(unittest.TestCase):
    def test_transparent_rgb_and_color_profile_survive_exactly(self):
        with workspace_directory() as directory:
            root = Path(directory)
            (root/'assets').mkdir()
            (root/'dist/src/data').mkdir(parents=True)
            source = root/'assets/alpha.png'
            image = Image.new('RGBA', (64,64))
            image.putdata([(37,59,91,0) if i%3==0 else (17,131,223,127) if i%3==1 else (222,99,13,255) for i in range(64*64)])
            profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
            image.save(source, compress_level=0, icc_profile=profile)
            before = source.read_bytes()
            (root/'inputs.json').write_text(json.dumps(['assets/alpha.png']))
            command = [sys.executable,str(ENCODER),'--root',str(root),'--dist',str(root/'dist'),'--inputs',str(root/'inputs.json')]
            subprocess.run(command,check=True,capture_output=True)
            report=json.loads((root/'dist/asset-encoding.json').read_text())
            self.assertEqual(report['converted'],1)
            target=root/'dist'/report['assets'][0]['file']
            with Image.open(target) as decoded:
                self.assertEqual(decoded.convert('RGBA').tobytes(),image.tobytes())
                self.assertEqual(decoded.info['icc_profile'],profile)
            self.assertEqual(source.read_bytes(),before)
            self.assertLess(target.stat().st_size,len(before))
            # A stale/corrupt cached derivative must not be silently reused.
            target.write_bytes(b'corrupted build output')
            subprocess.run(command+['--resume'],check=True,capture_output=True)
            with Image.open(target) as decoded:
                self.assertEqual(decoded.convert('RGBA').tobytes(),image.tobytes())

    def test_animation_and_high_bit_depth_remain_original_files(self):
        with workspace_directory() as directory:
            root=Path(directory)
            (root/'assets').mkdir()
            (root/'dist/src/data').mkdir(parents=True)
            Image.new('I;16',(8,8),513).save(root/'assets/depth.png')
            Image.new('RGBA',(8,8),'red').save(root/'assets/animated.png',save_all=True,append_images=[Image.new('RGBA',(8,8),'blue')],duration=50,loop=0)
            inputs=['assets/depth.png','assets/animated.png']
            before={p:(root/p).read_bytes() for p in inputs}
            (root/'inputs.json').write_text(json.dumps(inputs))
            subprocess.run([sys.executable,str(ENCODER),'--root',str(root),'--dist',str(root/'dist'),'--inputs',str(root/'inputs.json')],check=True,capture_output=True)
            report=json.loads((root/'dist/asset-encoding.json').read_text())
            self.assertEqual(report['converted'],0)
            for row in report['assets']:
                self.assertEqual((root/'dist'/row['file']).read_bytes(),before[row['source']])
                self.assertEqual((root/row['source']).read_bytes(),before[row['source']])

if __name__=='__main__':
    unittest.main()
