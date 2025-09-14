#!/usr/bin/env python3
"""
Modern SVG Sprite Generator for Icon System Optimization
Generates optimized SVG sprites from the Jinja icon registry
"""

import os
import re
from pathlib import Path

def extract_icon_registry():
    """Extract icon registry from the Jinja template"""
    icons_file = Path(__file__).parent.parent / "app/templates/macros/base/icons.html"
    
    if not icons_file.exists():
        print(f"Error: {icons_file} not found")
        return {}
    
    content = icons_file.read_text()
    
    # Extract the icon registry using regex
    registry_pattern = r"{% set icon_registry = \{(.*?)\} %}"
    match = re.search(registry_pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find icon_registry in template")
        return {}
    
    registry_content = match.group(1)
    
    # Parse individual icons
    icons = {}
    icon_pattern = r"'([^']+)':\s*\{[^}]*'path':\s*'([^']+)'[^}]*'type':\s*'([^']+)'[^}]*\}"
    
    for match in re.finditer(icon_pattern, registry_content):
        icon_name = match.group(1)
        path = match.group(2)
        icon_type = match.group(3)
        icons[icon_name] = {
            'path': path,
            'type': icon_type
        }
    
    return icons

def generate_svg_sprite(icons, output_path):
    """Generate optimized SVG sprite"""
    sprite_content = '''<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
'''
    
    for icon_name, icon_data in icons.items():
        fill_attr = 'fill="currentColor"' if icon_data['type'] == 'fill' else 'fill="none" stroke="currentColor"'
        stroke_attrs = 'stroke-linecap="round" stroke-linejoin="round" stroke-width="2"' if icon_data['type'] == 'stroke' else ''
        
        sprite_content += f'''  <symbol id="icon-{icon_name}" viewBox="0 0 24 24" {fill_attr}>
    <path {stroke_attrs} d="{icon_data['path']}"/>
  </symbol>
'''
    
    sprite_content += '</svg>\n'
    
    # Write sprite file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(sprite_content)
    
    return len(icons)

def generate_sprite_macro(icons, output_path):
    """Generate Jinja macro for using sprites"""
    macro_content = '''{% macro sprite_icon(name, size='lg', additional_class='') %}
{# Modern SVG Sprite Icon System - Optimized for Performance #}
<svg data-icon-size="{{ size }}" class="{{ additional_class }}" aria-hidden="true">
  <use href="#icon-{{ name }}"></use>
</svg>
{% endmacro %}

{% macro icon_sprite_loader() %}
{# Include the SVG sprite - call once in your base template #}
{% include 'static/icons/sprite.svg' %}
{% endmacro %}

{# Available icons in sprite: ''' + ', '.join(sorted(icons.keys())) + ''' #}
'''
    
    output_file = Path(output_path)
    output_file.write_text(macro_content)

def main():
    """Main sprite generation function"""
    print("🚀 Modern SVG Sprite Generator")
    print("=" * 50)
    
    # Extract icons from Jinja template
    print("📖 Reading icon registry from Jinja template...")
    icons = extract_icon_registry()
    
    if not icons:
        print("❌ No icons found in registry")
        return
    
    print(f"✅ Found {len(icons)} icons: {', '.join(sorted(icons.keys())[:5])}...")
    
    # Generate SVG sprite
    sprite_path = Path(__file__).parent.parent / "app/static/icons/sprite.svg"
    print(f"🎨 Generating SVG sprite: {sprite_path}")
    icon_count = generate_svg_sprite(icons, sprite_path)
    
    # Generate Jinja macro
    macro_path = Path(__file__).parent.parent / "app/templates/macros/base/sprite_icons.html"
    print(f"🔧 Generating Jinja macro: {macro_path}")
    generate_sprite_macro(icons, macro_path)
    
    print("=" * 50)
    print(f"✅ SVG Sprite system generated successfully!")
    print(f"📊 Icons processed: {icon_count}")
    print(f"📁 Sprite file: {sprite_path.relative_to(Path.cwd())}")
    print(f"🔧 Macro file: {macro_path.relative_to(Path.cwd())}")
    print("\nNext steps:")
    print("1. Include sprite in base template: {{ icon_sprite_loader() }}")
    print("2. Use sprites: {{ sprite_icon('plus', 'lg') }}")
    print("3. Consider switching to sprite system for better performance")

if __name__ == "__main__":
    main()