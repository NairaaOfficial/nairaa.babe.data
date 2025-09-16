import cv2
import numpy as np
import torch
from BSRGAN.models.network_rrdbnet import RRDBNet
from BSRGAN.utils import utils_image as util

# Load the pretrained BSRGAN model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_bsrgan = RRDBNet(3, 3, 64, 23, gc=32)
model_bsrgan.load_state_dict(torch.load('VIDEO_EDITING_QUALITY/BSRGAN/model_zoo/BSRGAN.pth'), strict=True)
model_bsrgan.eval()
model_bsrgan = model_bsrgan.to(device)

def enhance_frame_bsrgan(frame, log=False, index=None):
    try:
        if log and index is not None:
            print(f"🖼️ [BSRGAN] Enhancing frame {index}...")

        # Step 1: Convert BGR to RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        if log:
            print(f"🔄 [BSRGAN] Frame {index}: Converted BGR to normalized RGB")

        # Step 2: Convert to tensor and move to device
        img_tensor = torch.from_numpy(img_rgb.transpose(2, 0, 1)).unsqueeze(0).float().to(device)
        if log:
            print(f"📦 [BSRGAN] Frame {index}: Converted to tensor and moved to device")

        # Step 3: Model inference
        with torch.no_grad():
            output_tensor = model_bsrgan(img_tensor).clamp_(0, 1)
        if log:
            print(f"⚙️ [BSRGAN] Frame {index}: Inference done")

        # Step 4: Convert output tensor back to image
        output_img = output_tensor.squeeze().cpu().numpy().transpose(1, 2, 0)
        output_img = (output_img * 255.0).round().astype(np.uint8)
        if log:
            print(f"📤 [BSRGAN] Frame {index}: Converted output tensor to image")

        # Step 5: Convert RGB to BGR for OpenCV
        enhanced_frame = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)

        if log and index is not None:
            print(f"✅ [BSRGAN] Frame {index} enhanced successfully.")

        return enhanced_frame

    except Exception as e:
        print(f"❌ [BSRGAN] Error enhancing frame {index if index is not None else ''}: {e}")
        return frame  # Return original if enhancement fails