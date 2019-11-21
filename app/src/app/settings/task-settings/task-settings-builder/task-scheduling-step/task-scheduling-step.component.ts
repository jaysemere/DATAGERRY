/*
* DATAGERRY - OpenSource Enterprise CMDB
* Copyright (C) 2019 NETHINKS GmbH
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.

* You should have received a copy of the GNU Affero General Public License
* along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

import { Component, Input, OnInit } from '@angular/core';
import { CmdbMode } from '../../../../framework/modes.enum';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'cmdb-task-scheduling-step',
  templateUrl: './task-scheduling-step.component.html',
  styleUrls: ['./task-scheduling-step.component.scss']
})
export class TaskSchedulingStepComponent implements OnInit {

  @Input()
  set preData(data: any) {
    if (data !== undefined && data.scheduling !== undefined ) {
      this.eventForm.patchValue(data.scheduling.event);
    }
  }

  @Input() public mode: CmdbMode;
  public eventForm: FormGroup;


  constructor(private formBuilder: FormBuilder) {
    this.eventForm = this.formBuilder.group({
      active: new FormControl(false, Validators.required),
    });
  }

  ngOnInit() {
    if (this.mode === CmdbMode.Edit) {
      this.eventForm.markAllAsTouched();
    }
  }
}
