import os

import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty, IntProperty, PointerProperty
from bpy.utils import unregister_class, register_class

from . import properties
from .config import defaults as default

class selected_bounds(AddonPreferences):

  bl_idname = __name__.partition('.')[0]

  running = BoolProperty(
    name = 'Running',
    description = 'Used internally.',
    default = False
  )

  mode = EnumProperty(
    name = 'Display Mode',
    description = 'What objects to display bounds around.',
    items = [
      ('NONE', 'None', 'Disable selected bounds.'),
      ('SELECTED', 'Selected Objects', 'The selected objects.'),
      ('ACTIVE', 'Active Object', 'The active object.'),
    ],
    default = default['mode']
  )

  color = FloatVectorProperty(
    name = 'Color',
    description = 'Color of the bounds.',
    subtype = 'COLOR',
    size = 4,
    min = 0.0,
    max = 1.0,
    default = default['color']
  )

  use_object_color = BoolProperty(
    name = 'Use Object Color',
    description = 'Use the object\'s color.',
    default = default['use_object_color']
  )

  width = IntProperty(
    name = 'Pixel Width',
    description = 'Width of the lines in pixels.',
    min = 1,
    max = 20,
    subtype = 'PIXEL',
    default = default['width']
  )

  length = IntProperty(
    name = 'Length',
    description = 'Length of the lines as they extend from the corners.',
    min = 10,
    max = 100,
    subtype = 'PERCENTAGE',
    default = default['length']
  )

  scene_independent = BoolProperty(
    name = 'Independent Scene Options',
    description = 'Use independent scene options in the viewport rather then using these preferences.',
    default = default['scene_independent']
  )

  display_preferences = BoolProperty(
    name = 'Display Preferences',
    description = 'Display these preferences in the 3D view\'s display panel instead.',
    default = default['display_preferences']
  )

  def draw(self, context):

    layout = self.layout

    column = layout.column()
    column.enabled = not context.window_manager.running_modal.selected_bounds
    column.scale_y = 2

    text = 'Enable' if not context.window_manager.running_modal.selected_bounds else 'Running'
    column.operator('view3d.selected_bounds', text=text)

    column = layout.column()

    box = layout.box()

    column = box.column()

    row = column.row(align=True)

    row.prop(self, 'mode')

    sub = row.row(align=True)
    sub.scale_x = 0.5
    sub.prop(self, 'color', text='')

    subsub = sub.row(align=True)
    subsub.scale_x = 2
    subsub.prop(self, 'use_object_color', text='', icon='OBJECT_DATA')

    row = box.row()

    row.prop(self, 'width')
    row.prop(self, 'length', slider=True)

    row = box.row()
    row.prop(self, 'scene_independent')

    sub = row.row()
    sub.enabled = not self.scene_independent
    sub.prop(self, 'display_preferences')

    row = box.row()
    row.alignment = 'RIGHT'
    row.scale_y = 1.5

    row.operator('wm.update_selected_bound_settings')
    row.operator('wm.save_selected_bound_defaults')


class update(Operator):
  bl_idname = 'wm.update_selected_bound_settings'
  bl_label = 'Update'
  bl_description = 'Update the 3D view with the current preference values.'
  bl_options = {'INTERNAL'}


  @classmethod
  def poll(operator, context):

    return context.user_preferences.addons[__name__.partition('.')[0]].preferences.scene_independent


  def execute(self, context):

    preference = context.user_preferences.addons[__name__.partition('.')[0]].preferences

    for scene in bpy.data.scenes:

      option = scene.selected_bounds

      option.mode = preference.mode
      option.color = preference.color
      option.use_object_color = preference.use_object_color
      option.width = preference.width
      option.length = preference.length

    return {'FINISHED'}


class save(Operator):
  bl_idname = 'wm.save_selected_bound_defaults'
  bl_label = 'Save'
  bl_description = 'Permanently store the current settings as the default values. (Requires Restart)'
  bl_options = {'INTERNAL'}


  def execute(self, context):

    preference = context.user_preferences.addons[__name__.partition('.')[0]].preferences

    defaults = {
      'mode': preference.mode,
      'color': preference.color[:],
      'use_object_color': preference.use_object_color,
      'width': preference.width,
      'length': preference.length,
      'scene_independent': preference.scene_independent,
      'display_preferences': preference.display_preferences,
    }

    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.py'))

    with open(filepath, '+r') as config:
      config.truncate()
      config.write('# Generated by preferences.save\ndefaults = {}'.format(str(defaults)))

    return {'FINISHED'}
