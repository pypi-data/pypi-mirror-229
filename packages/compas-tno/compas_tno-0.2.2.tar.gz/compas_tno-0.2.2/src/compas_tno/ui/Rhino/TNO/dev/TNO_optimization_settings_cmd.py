from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_tno.optimisers import Optimiser
from compas_tno.rhino import OptimiserObject
from compas_tno.rhino import SettingsForm


__commandname__ = "TNO_optimization_settings"


def RunCommand(is_interactive):

    if 'TNO' not in sc.sticky:
        compas_rhino.display_message('TNO has not been initialised yet.')
        return

    scene = sc.sticky['TNO']['scene']

    objects = scene.find_by_name('Optimiser')
    if not objects:
        optimiser = Optimiser()
        scene.add(optimiser, name='Optimiser', layer=None)
        objects = scene.find_by_name('Optimiser')
        optimiserobject = objects[0]
        optimiserobject.update_object_from_optimiser()

    SettingsForm.from_scene(scene, object_types=[OptimiserObject])

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':

    RunCommand(True)
