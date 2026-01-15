#!/usr/bin/env python
"""
Generate reference stain profiles from a set of good quality images.

Usage:
    python setup_reference_profiles.py --stain_type HE --image_dir /path/to/good/he/images
"""
import argparse
import os
import json
import numpy as np
from PIL import Image
from pipeline.od import rgb_to_od
from pipeline.stain import estimate_stain_vectors_macenko, extract_stain_concentrations
from pipeline.normalize import generate_reference_profile


def load_images_from_directory(image_dir):
    """Load all images from directory"""
    images = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
    
    for filename in os.listdir(image_dir):
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            filepath = os.path.join(image_dir, filename)
            try:
                img = Image.open(filepath)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_array = np.array(img)
                images.append(img_array)
                print(f"Loaded: {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return images


def generate_profile_from_images(images, stain_type):
    """Generate reference profile from images"""
    print(f"Processing {len(images)} images for {stain_type} stain...")
    
    concentrations_list = []
    
    for i, rgb_image in enumerate(images):
        print(f"Processing image {i+1}/{len(images)}...")
        
        # Convert to OD
        od_image = rgb_to_od(rgb_image)
        
        # Estimate stain vectors
        stain_vectors = estimate_stain_vectors_macenko(od_image)
        
        # Extract concentrations
        concentrations = extract_stain_concentrations(od_image, stain_vectors)
        concentrations_list.append(concentrations)
    
    # Generate reference statistics
    reference_stats = generate_reference_profile(concentrations_list)
    reference_stats['stain_type'] = stain_type
    
    return reference_stats


def main():
    parser = argparse.ArgumentParser(description='Generate reference stain profiles')
    parser.add_argument('--stain_type', required=True, choices=['HE', 'IHC', 'PAP'],
                        help='Stain type')
    parser.add_argument('--image_dir', required=True,
                        help='Directory containing good quality images')
    parser.add_argument('--output_dir', default='configs/reference_stain_profiles',
                        help='Output directory for reference profiles')
    
    args = parser.parse_args()
    
    # Load images
    images = load_images_from_directory(args.image_dir)
    
    if len(images) == 0:
        print(f"Error: No images found in {args.image_dir}")
        return
    
    # Generate profile
    reference_stats = generate_profile_from_images(images, args.stain_type)
    
    # Save profile
    os.makedirs(args.output_dir, exist_ok=True)
    output_file = os.path.join(args.output_dir, f'{args.stain_type.lower()}_reference.json')
    
    with open(output_file, 'w') as f:
        json.dump(reference_stats, f, indent=2)
    
    print(f"\nReference profile saved to: {output_file}")
    print("\nProfile statistics:")
    print(f"  Stain 0 mean: {reference_stats['stain_0_mean']:.4f}")
    print(f"  Stain 0 std:  {reference_stats['stain_0_std']:.4f}")
    print(f"  Stain 1 mean: {reference_stats['stain_1_mean']:.4f}")
    print(f"  Stain 1 std:  {reference_stats['stain_1_std']:.4f}")


if __name__ == '__main__':
    main()
