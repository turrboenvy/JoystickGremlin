# -*- coding: utf-8; -*-

# Copyright (C) 2015 - 2023 Lionel Ott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import annotations

import uuid

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from PySide6 import QtCore, QtQml
from PySide6.QtCore import Property, Signal, Slot

import gremlin.profile
from gremlin.signal import signal
from gremlin.base_classes import DataInsertionMode
from gremlin.error import GremlinError
from gremlin.types import AxisButtonDirection, HatDirection, InputType
from gremlin.util import clamp
from gremlin.plugin_manager import PluginManager

from gremlin.ui.action_model import ActionModel, SequenceIndex

if TYPE_CHECKING:
    from action_plugins.root import RootModel
    from gremlin.base_classes import AbstractActionData


QML_IMPORT_NAME = "Gremlin.Profile"
QML_IMPORT_MAJOR_VERSION = 1


@QtQml.QmlElement
class VirtualButtonModel(QtCore.QObject):

    """Represents both axis and hat virtual buttons."""

    lowerLimitChanged = Signal()
    upperLimitChanged = Signal()
    directionChanged = Signal()
    hatDirectionChanged = Signal()

    def __init__(
        self,
        virtual_button: gremlin.profile.AbstractVirtualButton,
        parent: Optional[QtCore.QObject]=None
    ):
        """Creates a new instance.

        Args:
            virtual_button: the profile class representing the instance's data
            parent: parent object of the widget
        """
        super().__init__(parent)

        self.virtual_button = virtual_button

    def _get_lower_limit(self) -> float:
        return self.virtual_button.lower_limit

    def _set_lower_limit(self, value: float) -> None:
        if value != self.virtual_button.lower_limit:
            self.virtual_button.lower_limit = clamp(value, -1.0, 1.0)
            self.lowerLimitChanged.emit()

    def _get_upper_limit(self) -> float:
        return self.virtual_button.upper_limit

    def _set_upper_limit(self, value: float) -> None:
        if value != self.virtual_button.upper_limit:
            self.virtual_button.upper_limit = clamp(value, -1.0, 1.0)
            self.upperLimitChanged.emit()

    def _get_direction(self) -> str:
        return AxisButtonDirection.to_string(self.virtual_button.direction)

    def _set_direction(self, value: str) -> None:
        direction = AxisButtonDirection.to_enum(value.lower())
        if direction != self.virtual_button.direction:
            self.virtual_button.direction = direction
            self.directionChanged.emit()

    def _get_hat_state(self, hat_direction):
        return hat_direction in self.virtual_button.directions

    def _set_hat_state(self, hat_direction, is_active):
        if is_active:
            if hat_direction not in self.virtual_button.directions:
                self.virtual_button.directions.append(hat_direction)
                self.hatDirectionChanged.emit()
        else:
            if hat_direction in self.virtual_button.directions:
                index = self.virtual_button.directions.index(hat_direction)
                del self.virtual_button.directions[index]
                self.hatDirectionChanged.emit()

    lowerLimit = Property(
        float,
        fget=_get_lower_limit,
        fset=_set_lower_limit,
        notify=lowerLimitChanged
    )
    upperLimit = Property(
        float,
        fget=_get_upper_limit,
        fset=_set_upper_limit,
        notify=upperLimitChanged
    )
    direction = Property(
        str,
        fget=_get_direction,
        fset=_set_direction,
        notify=directionChanged
    )

    hatNorth = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.North),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.North, x),
        notify=hatDirectionChanged
    )
    hatNorthEast = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.NorthEast),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.NorthEast, x),
        notify=hatDirectionChanged
    )
    hatEast = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.East),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.East, x),
        notify=hatDirectionChanged
    )
    hatSouthEast = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.SouthEast),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.SouthEast, x),
        notify=hatDirectionChanged
    )
    hatSouth = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.South),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.South, x),
        notify=hatDirectionChanged
    )
    hatSouthWest = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.SouthWest),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.SouthWest, x),
        notify=hatDirectionChanged
    )
    hatWest = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.West),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.West, x),
        notify=hatDirectionChanged
    )
    hatNorthWest = Property(
        bool,
        fget=lambda cls: VirtualButtonModel._get_hat_state(cls, HatDirection.NorthWest),
        fset=lambda cls, x: VirtualButtonModel._set_hat_state(cls, HatDirection.NorthWest, x),
        notify=hatDirectionChanged
    )


@QtQml.QmlElement
class HatDirectionModel(QtCore.QObject):

    """QML model representing the directions of a hat."""

    directionsChanged = Signal()

    def __init__(
        self,
        directions: List[HatDirection],
        parent: Optional[QtCore.QObject]=None
    ):
        super().__init__(parent)

        self.directions = directions

    def _get_hat_state(self, direction: HatDirection) -> bool:
        return direction in self.directions

    def _set_hat_state(self, direction: HatDirection, is_active: bool) -> None:
        if is_active:
            if direction not in self.directions:
                self.directions.append(direction)
                self.directionsChanged.emit()
        else:
            if direction in self.directions:
                index = self.directions.index(direction)
                del self.directions[index]
                self.directionsChanged.emit()

    hatNorth = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.North),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.North, x),
        notify=directionsChanged
    )
    hatNorthEast = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.NorthEast),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.NorthEast, x),
        notify=directionsChanged
    )
    hatEast = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.East),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.East, x),
        notify=directionsChanged
    )
    hatSouthEast = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.SouthEast),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.SouthEast, x),
        notify=directionsChanged
    )
    hatSouth = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.South),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.South, x),
        notify=directionsChanged
    )
    hatSouthWest = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.SouthWest),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.SouthWest, x),
        notify=directionsChanged
    )
    hatWest = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.West),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.West, x),
        notify=directionsChanged
    )
    hatNorthWest = Property(
        bool,
        fget=lambda cls: HatDirectionModel._get_hat_state(cls, HatDirection.NorthWest),
        fset=lambda cls, x: HatDirectionModel._set_hat_state(cls, HatDirection.NorthWest, x),
        notify=directionsChanged
    )


@QtQml.QmlElement
class InputItemModel(QtCore.QObject):

    """QML model class representing an InputItem instance."""

    bindingsChanged = Signal()

    def __init__(self, input_item: gremlin.profile.InputItem, parent=None):
        super().__init__(parent)

        self._input_item = input_item

    @Property(QtCore.QObject, notify=bindingsChanged)
    def inputItemBindings(self) -> InputItemBindingListModel:
        return InputItemBindingListModel(
            self._input_item.action_sequences,
            self
        )

    @Slot()
    def createNewActionSequence(self) -> None:
        # Create root action
        action = PluginManager().create_instance(
            "Root",
            self._input_item.input_type
        )

        # Create binding instance and add it to the input item
        binding = gremlin.profile.InputItemBinding(self._input_item)
        binding.root_action = action
        binding.behavior = self._input_item.input_type

        self._input_item.action_sequences.append(binding)
        self.bindingsChanged.emit()

    @Slot(str, str, str)
    def dropAction(self, source: str, target: str, method: str) -> None:
        """Handles dropping an action tree element

        Args:
            source: identifier of the tree being dropped
            target: identifier of the location on which the source is dropped
            method: type of drop action to perform
        """
        # Force a UI refresh without performing any model changes if both
        # source and target item are identical, i.e. an invalid drag&drop
        if source == target:
            self.bindingsChanged.emit()
            return

        source_id = uuid.UUID(source)
        target_id = uuid.UUID(target)
        source_entry = None
        for idx, entry in enumerate(self._input_item.action_sequences):
            if entry.root_action.id == source_id:
                source_entry = self._input_item.action_sequences.pop(idx)
        if source_entry is not None:
            for idx, entry in enumerate(self._input_item.action_sequences):
                if entry.root_action.id == target_id:
                    self._input_item.action_sequences.insert(idx+1, source_entry)

        self.bindingsChanged.emit()


@QtQml.QmlElement
class InputItemBindingModel(QtCore.QObject):

    """Model representing an ActionTree instance."""

    behaviorChanged = Signal()
    descriptionChanged = Signal()
    virtualButtonChanged = Signal()
    actionCountChanged = Signal()
    rootActionChanged = Signal()
    inputTypeChanged = Signal()

    def __init__(
            self,
            input_item_binding: gremlin.profile.InputItemBinding,
            parent=None
    ):
        super().__init__(parent)

        self._input_item_binding = input_item_binding
        self._virtual_button_model = VirtualButtonModel(
            self._input_item_binding.virtual_button
        )

        self._action_models = {}
        self._index_lookup = {}
        self._child_lookup = {}
        self._container_index_lookup = {}
        self._create_action_models()

    def _create_action_models(self) -> None:
        # Reset storage
        self._action_models = {}
        self._index_lookup = {}
        self._child_lookup = {}
        self._container_index_lookup = {}

        # Initialize action queue
        actions = [(self.root_action, None), ]
        parent_indices = [SequenceIndex(None, None, None),]
        container_indices = [0, ]
        count = 0

        while len(actions) > 0:
            # Grab first item from the queue
            action, container = actions.pop(0)
            parent_index = parent_indices.pop(0)
            container_index = container_indices.pop(0)

            # Create model for the action and store it
            index = SequenceIndex(parent_index.index, container, count)
            model = action.model(action, self, index, parent_index, self)
            self._action_models[index] = model
            self._index_lookup[index.index] = index
            self._container_index_lookup[index] = container_index
            key = (index.parent_index, index.container_name)
            if key not in self._child_lookup:
                self._child_lookup[key] = []
            self._child_lookup[key].append(model)

            # Add all children to the list of items to process
            c_actions, c_containers = action.get_actions()
            c_index = 0
            for i in range(len(c_actions)):
                actions.append((c_actions[i], c_containers[i]))
                parent_indices.append(index)
                if i > 0:
                    if c_containers[i] != c_containers[i-1]:
                        c_index = 0
                container_indices.append(c_index)
                c_index += 1

            count += 1

    def get_child_actions(
            self,
            index: SequenceIndex | int,
            container: str
    ) -> List[ActionModel]:
        if isinstance(index, int):
            index = self._index_lookup[index]
        return self._child_lookup.get((index.index, container), [])

    def get_action_model_by_sidx(self, sidx: int) -> ActionModel:
        if sidx not in self._index_lookup:
            raise GremlinError(f"No action with sequence index {sidx} exists")
        return self._action_models[self._index_lookup[sidx]]

    def get_action_container_index(self, index: SequenceIndex) -> int:
        """Returns the linear index into the container storing the action.

        Args:
            index: sequence index of the action

        Returns:
            Linear index into the container holding the action
        """
        return self._container_index_lookup[index]

    def sync_data(self) -> None:
        self._create_action_models()
        self.rootActionChanged.emit()

    def action_information(
            self,
            index: int
    ) -> Tuple[str, AbstractActionData, AbstractActionData]:
        """Returns the action model corresponding to the given index.

        Args:
            index: sequence index of the action to return

        Returns:
            ActionModel corresponding to the given index
        """
        if index not in self._index_lookup:
            raise GremlinError(f"No action with provided index: {index}")
        return self._action_models[self._index_lookup[index]].data

    def move_action(
            self,
            source_idx: int,
            target_idx: int,
            container: Optional[str]=None
    ) -> None:
        """Moves the source action to the spot after the target action.

        If a container name is given then the source action will be appended to
        the container with the given name of the target action.

        Args:
            source_idx: sequence index of the action to move
            target_idx: sequence index of the action after which to place the
                moved action
            container: name of the container to insert the action into
        """
        s_model = self.get_action_model_by_sidx(source_idx)
        t_model = self.get_action_model_by_sidx(target_idx)

        s_parent_identifier = (
            s_model.sequence_index.parent_index,
            s_model.sequence_index.container_name
        )
        t_parent_identifier = (
            t_model.sequence_index.parent_index,
            t_model.sequence_index.container_name
        )

        if container is not None:
            self.remove_action(s_model.sequence_index, False)
            self.append_action(
                s_model.action_data,
                t_model.sequence_index,
                container
            )
        else:
            # If source and target are in the same container special care has to
            # be taken to ensure removal and insertion happen in a valid order
            move_performed = False
            if s_parent_identifier == t_parent_identifier:
                # Determine container indices of the source and target actions
                s_lid = self.get_action_container_index(s_model.sequence_index)
                t_lid = self.get_action_container_index(t_model.sequence_index)

                # Perform the action that affects a change in the rear part
                # of the container
                if s_lid < t_lid:
                    move_performed = True
                    self.append_action(
                        s_model.action_data,
                        t_model.sequence_index
                    )
                    self.remove_action(s_model.sequence_index, False)

            # This is the default case if the source and target actions are part
            # of different parent actions or containers. Also if the source
            # action is after the target action, performing the removal first
            # is safe.
            if not move_performed:
                self.remove_action(s_model.sequence_index, False)
                self.append_action(s_model.action_data, t_model.sequence_index)

        self._create_action_models()
        self.rootActionChanged.emit()

    def remove_action(
            self,
            action_index: int | SequenceIndex,
            perform_sync: bool=True
    ) -> None:
        """Removes the specified action from its parent.

        The provided action_index can be either a SequenceIndex instance or an
        integer corresponding to the unique index of the action.

        Args:
            action_index: index identifying the action to remove
            perform_sync: if True data will be resynchronized and a change
                event emitted
        """
        if isinstance(action_index, int):
            action_index = self._index_lookup[action_index]

        parent_data = \
            self.get_action_model_by_sidx(action_index.parent_index).action_data
        parent_data.remove_action(
            self.get_action_container_index(action_index),
            action_index.container_name
        )

        if perform_sync:
            self._create_action_models()
            self.rootActionChanged.emit()

    def append_action(
            self,
            action_data: AbstractActionData,
            target_index: SequenceIndex,
            container: Optional[str]=None
    ) -> None:
        """Appends the provided action data after the specified action.

        Args:
            action_data: data of the action to append
            target_index: sequence index of the action after which to insert
                the new action's data
        """
        # If the parent index of the target is None the target is the single
        # RootAction and thus should be used to insert into directly.
        if target_index.parent_index is None:
            data = self.get_action_model_by_sidx(target_index.index).action_data
            data.insert_action(
                action_data,
                "children",
                DataInsertionMode.Prepend,
                0
            )
        elif container is None:
            parent_data = self.get_action_model_by_sidx(
                target_index.parent_index
            ).action_data
            parent_data.insert_action(
                action_data,
                target_index.container_name,
                DataInsertionMode.Append,
                self.get_action_container_index(target_index)
            )
        else:
            target_data = self.get_action_model_by_sidx(
                target_index.index
            ).action_data
            target_data.insert_action(
                action_data,
                container,
                DataInsertionMode.Prepend,
                0
            )

    def is_last_action_in_container(self, index: SequenceIndex) -> bool:
        """Returns whether the specified action is the last one in a container.

        Args:
            index: SequenceIndex corresponding to an action

        Returns:
            True if the specified action is the last one in its container, False
            otherwise.
        """
        indices = sorted([
            self._container_index_lookup[m.sequence_index]
            for m in self.get_child_actions(
                index.parent_index,
                index.container_name
            )
        ])
        return self._container_index_lookup[index] >= indices[-1]

    @Slot()
    def deleteActionSequence(self) -> None:
        self._input_item_binding.input_item.remove_item_binding(
            self._input_item_binding
        )
        signal.reloadUi.emit()

    @Property(type=str, notify=inputTypeChanged)
    def inputType(self) -> str:
        return InputType.to_string(
            self._input_item_binding.input_item.input_type
        )

    @Property(type=VirtualButtonModel, notify=virtualButtonChanged)
    def virtualButton(self) -> VirtualButtonModel:
        return self._virtual_button_model

    @Property(type=ActionModel, notify=rootActionChanged)
    def rootAction(self) -> RootModel:
        return self._action_models[self._index_lookup[0]]

    @property
    def root_action(self) -> AbstractActionData:
        return self._input_item_binding.root_action

    @property
    def input_item_binding(self) -> gremlin.profile.InputItemBinding:
        return self._input_item_binding

    def _get_behavior(self) -> str:
        return InputType.to_string(self._input_item_binding.behavior)

    def _set_behavior(self, text: str) -> None:
        behavior = InputType.to_enum(text)
        if behavior != self._input_item_binding.behavior:
            self._input_item_binding.behavior = behavior
            self._input_item_binding.virtual_button = None

            # Ensure a virtual button instance exists of the correct type
            # if one is needed
            input_type = self._input_item_binding.input_item.input_type
            if input_type == InputType.JoystickAxis and \
                    behavior == InputType.JoystickButton:
                if not isinstance(
                        self._input_item_binding.virtual_button,
                        gremlin.profile.VirtualAxisButton
                ):
                    self._input_item_binding.virtual_button = \
                        gremlin.profile.VirtualAxisButton()
                    self._virtual_button_model = VirtualButtonModel(
                        self._input_item_binding.virtual_button
                    )
            elif input_type == InputType.JoystickHat and \
                    behavior == InputType.JoystickButton:
                if not isinstance(
                        self._input_item_binding.virtual_button,
                        gremlin.profile.VirtualHatButton
                ):
                    self._input_item_binding.virtual_button = \
                        gremlin.profile.VirtualHatButton()
                    self._virtual_button_model = VirtualButtonModel(
                        self._input_item_binding.virtual_button
                    )

            # Update input type of all actions
            for model in self._action_models.values():
                model.action_data.set_behavior_type(behavior)

            # Force full redraw of the action
            self.behaviorChanged.emit()
            self.rootActionChanged.emit()
            # This one might be overkill
            signal.reloadUi.emit()

    def _get_description(self) -> str:
        return self._input_item_binding.description

    def _set_description(self, description: str) -> None:
        if description != self._input_item_binding.description:
            self._input_item_binding.description = description
            self.descriptionChanged.emit()

    @property
    def behavior_type(self):
        return self._input_item_binding.behavior

    behavior = Property(
        str,
        fget=_get_behavior,
        fset=_set_behavior,
        notify=behaviorChanged
    )

    description = Property(
        str,
        fget=_get_description,
        fset=_set_description,
        notify=descriptionChanged
    )


@QtQml.QmlElement
class InputItemBindingListModel(QtCore.QAbstractListModel):

    """List model of all InputItemBinding instances of a single input item."""

    # This fake single role and the roleName function are needed to have the
    # modelData property available in the QML delegate
    roles = {
        QtCore.Qt.UserRole + 1: QtCore.QByteArray("fake".encode()),
    }

    def __init__(
        self,
        items: List[gremlin.profile.InputItemBinding],
        parent=None
    ):
        super().__init__(parent)

        self._action_configurations = items

    def rowCount(self, parent: QtCore.QModelIndex=...) -> int:
        return len(self._action_configurations)

    def data(self, index: QtCore.QModelIndex, role: int=...) -> Any:
        return InputItemBindingModel(
            self._action_configurations[index.row()],
            parent=self
        )

    def roleNames(self) -> Dict:
        return InputItemBindingListModel.roles
