function geocoder_submit(formId, subId){
            const form = document.querySelector("#form-"+formId);
            const formTrigger = form.querySelector("#" + subId);
            //const formTrigger = document.querySelector("#" + subId);
            const submitEvent = new SubmitEvent("submit", { submitter: formTrigger });
            form.dispatchEvent(submitEvent);
        }

L.Control.BingGeocoder = L.Control.extend({
	options: {
		collapsed: true,
		position: 'topright',
		text: 'Locate',
        geocoderId: 0,
		callback: function (results) {
			var bbox = results.resourceSets[0].resources[0].bbox,
				first = new L.LatLng(bbox[0], bbox[1]),
				second = new L.LatLng(bbox[2], bbox[3]),
				bounds = new L.LatLngBounds([first, second]);
			this._map.fitBounds(bounds);
		}
	},

	_callbackId: 0,

	initialize: function (key, options) {
		this.key = key;
		L.Util.setOptions(this, options);
	},

	onAdd: function (map) {
		this._map = map;
		var className = 'leaflet-control-geocoder',
			container = this._container = L.DomUtil.create('div', className);

		L.DomEvent.disableClickPropagation(container);

		var form = this._form = L.DomUtil.create('form', className + '-form');

		var input = this._input = L.DomUtil.create('input', className + '-input', form);
		input.type = 'text';
        refID = className + '-' + this.options.geocoderId;
        input.setAttribute("onkeydown", 'if (event.keyCode == 13) {geocoder_submit(\'' +this.options.geocoderId+'\','+'\''+refID+'\')}');

		var submit = this._createButton(className, this.options.text);
		form.appendChild(submit);

		L.DomEvent.on(form, 'submit', this._geocode, this);

		if (this.options.collapsed) {
			L.DomEvent.on(container, 'mouseover', this._expand, this);
			L.DomEvent.on(container, 'mouseout', this._collapse, this);

			var link = this._layersLink = L.DomUtil.create('a', className + '-toggle', container);
			link.href = '#';
			link.title = 'Bing Geocoder';

			L.DomEvent.on(link, L.Browser.touch ? 'click' : 'focus', this._expand, this);

			this._map.on('movestart', this._collapse, this);
		} else {
			this._expand();
		}

        form.id = 'form-' + this.options.geocoderId;
		container.appendChild(form);

		return container;
	},
    
	_createButton: function(css, text) {
        refID = css + '-' + this.options.geocoderId;
        
		var btn = '<button type="submit" class="' + css + '-button" id="'+refID+'" /><div onclick="javascript:geocoder_submit(\'' +this.options.geocoderId+'\','+'\''+refID+'\')">' + text + '</div></button>';

		var radioFragment = document.createElement('div');
		radioFragment.innerHTML = btn;

		return radioFragment.firstChild;
	},

	_geocode : function (event) {
		L.DomEvent.preventDefault(event);
		this._callbackId = '_l_binggeocoder_' + (this._callbackId++);
		window[this._callbackId] = L.Util.bind(this.options.callback, this);

		var params = {
			query: this._input.value,
			key : this.key,
			jsonp : this._callbackId
		},
		url = 'https://dev.virtualearth.net/REST/v1/Locations' + L.Util.getParamString(params),
		script = L.DomUtil.create('script', '', document.getElementsByTagName('head')[0]);

		script.type = 'text/javascript';
		script.src = url;
		script.id = this._callbackId;
	},

	_expand: function () {
		L.DomUtil.addClass(this._container, 'leaflet-control-geocoder-expanded');
	},

	_collapse: function () {
		L.DomUtil.removeClass(this._container, 'leaflet-control-geocoder-expanded');
	}
});

L.control.bingGeocoder = function (key, options) {
		return new L.Control.BingGeocoder(key, options);
};