// -*- coding: utf-8; -*-
//
// Copyright (C) 2015 - 2022 Lionel Ott
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Gremlin.Config


Item {
    id: _root

    property ConfigGroupModel groupModel

    ListView {
        id: _groupView

        width: parent.width
        height: parent.height

        model: groupModel
        delegate: _groupDelegate
    }

    Component {
        id: _groupDelegate

        Item {
            required property int index
            required property ConfigEntryModel entryModel

            width: _groupView.width
            height: 200//_entryView.height

            // title: "Something" + index

            Column {
                Repeater {
                    id: _entryView

                    model: entryModel
                    delegate: _entryDelegate
                }

            }
        }
    }

    Component {
        id: _entryDelegate

        Label {
            required property int index
            required property string description

            height: 20
            width: 500//ListView.view.width

            text: description
            color: "#008AD8"
        }
    }
}