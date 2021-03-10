(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('leaflet')) :
    typeof define === 'function' && define.amd ? define(['exports', 'leaflet'], factory) :
    (global = global || self, factory(global.LeafletLasso = {}, global.L));
}(this, function (exports, L) { 'use strict';

    L = L && L.hasOwnProperty('default') ? L['default'] : L;

    /*! *****************************************************************************
    Copyright (c) Microsoft Corporation. All rights reserved.
    Licensed under the Apache License, Version 2.0 (the "License"); you may not use
    this file except in compliance with the License. You may obtain a copy of the
    License at http://www.apache.org/licenses/LICENSE-2.0

    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
    WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
    MERCHANTABLITY OR NON-INFRINGEMENT.

    See the Apache Version 2.0 License for specific language governing permissions
    and limitations under the License.
    ***************************************************************************** */
    /* global Reflect, Promise */

    var extendStatics = function(d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };

    function __extends(d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    }

    var __assign = function() {
        __assign = Object.assign || function __assign(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };

    var LassoPolygon = /** @class */ (function (_super) {
        __extends(LassoPolygon, _super);
        function LassoPolygon(latlngs, options) {
            var _this = _super.call(this) || this;
            _this.polyline = L.polyline(latlngs, options);
            _this.polygon = L.polygon(latlngs, __assign({}, options, { weight: 0 }));
            return _this;
        }
        LassoPolygon.prototype.onAdd = function (map) {
            this.polyline.addTo(map);
            this.polygon.addTo(map);
            return this;
        };
        LassoPolygon.prototype.onRemove = function () {
            this.polyline.remove();
            this.polygon.remove();
            return this;
        };
        LassoPolygon.prototype.addLatLng = function (latlng) {
            this.polyline.addLatLng(latlng);
            this.polygon.addLatLng(latlng);
            return this;
        };
        LassoPolygon.prototype.getLatLngs = function () {
            return this.polygon.getLatLngs()[0];
        };
        LassoPolygon.prototype.toGeoJSON = function () {
            return this.polygon.toGeoJSON();
        };
        return LassoPolygon;
    }(L.Layer));

    var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

    function createCommonjsModule(fn, module) {
    	return module = { exports: {} }, fn(module, module.exports), module.exports;
    }

    var terraformer = createCommonjsModule(function (module, exports) {
    (function (root, factory) {

      // Node.
      {
        exports = module.exports = factory();
      }

      // Browser Global.
      if(typeof window === "object") {
        root.Terraformer = factory();
      }

    }(commonjsGlobal, function(){
      var exports = {},
          EarthRadius = 6378137,
          DegreesPerRadian = 57.295779513082320,
          RadiansPerDegree =  0.017453292519943,
          MercatorCRS = {
            "type": "link",
            "properties": {
              "href": "http://spatialreference.org/ref/sr-org/6928/ogcwkt/",
              "type": "ogcwkt"
            }
          },
          GeographicCRS = {
            "type": "link",
            "properties": {
              "href": "http://spatialreference.org/ref/epsg/4326/ogcwkt/",
              "type": "ogcwkt"
            }
          };

      /*
      Internal: isArray function
      */
      function isArray(obj) {
        return Object.prototype.toString.call(obj) === "[object Array]";
      }

      /*
      Internal: safe warning
      */
      function warn() {
        var args = Array.prototype.slice.apply(arguments);

        if (typeof console !== undefined && console.warn) {
          console.warn.apply(console, args);
        }
      }

      /*
      Internal: Extend one object with another.
      */
      function extend(destination, source) {
        for (var k in source) {
          if (source.hasOwnProperty(k)) {
            destination[k] = source[k];
          }
        }
        return destination;
      }

      /*
      Public: Calculate an bounding box for a geojson object
      */
      function calculateBounds (geojson) {
        if(geojson.type){
          switch (geojson.type) {
            case 'Point':
              return [ geojson.coordinates[0], geojson.coordinates[1], geojson.coordinates[0], geojson.coordinates[1]];

            case 'MultiPoint':
              return calculateBoundsFromArray(geojson.coordinates);

            case 'LineString':
              return calculateBoundsFromArray(geojson.coordinates);

            case 'MultiLineString':
              return calculateBoundsFromNestedArrays(geojson.coordinates);

            case 'Polygon':
              return calculateBoundsFromNestedArrays(geojson.coordinates);

            case 'MultiPolygon':
              return calculateBoundsFromNestedArrayOfArrays(geojson.coordinates);

            case 'Feature':
              return geojson.geometry? calculateBounds(geojson.geometry) : null;

            case 'FeatureCollection':
              return calculateBoundsForFeatureCollection(geojson);

            case 'GeometryCollection':
              return calculateBoundsForGeometryCollection(geojson);

            default:
              throw new Error("Unknown type: " + geojson.type);
          }
        }
        return null;
      }

      /*
      Internal: Calculate an bounding box from an nested array of positions
      [
        [
          [ [lng, lat],[lng, lat],[lng, lat] ]
        ]
        [
          [lng, lat],[lng, lat],[lng, lat]
        ]
        [
          [lng, lat],[lng, lat],[lng, lat]
        ]
      ]
      */
      function calculateBoundsFromNestedArrays (array) {
        var x1 = null, x2 = null, y1 = null, y2 = null;

        for (var i = 0; i < array.length; i++) {
          var inner = array[i];

          for (var j = 0; j < inner.length; j++) {
            var lonlat = inner[j];

            var lon = lonlat[0];
            var lat = lonlat[1];

            if (x1 === null) {
              x1 = lon;
            } else if (lon < x1) {
              x1 = lon;
            }

            if (x2 === null) {
              x2 = lon;
            } else if (lon > x2) {
              x2 = lon;
            }

            if (y1 === null) {
              y1 = lat;
            } else if (lat < y1) {
              y1 = lat;
            }

            if (y2 === null) {
              y2 = lat;
            } else if (lat > y2) {
              y2 = lat;
            }
          }
        }

        return [x1, y1, x2, y2 ];
      }

      /*
      Internal: Calculate a bounding box from an array of arrays of arrays
      [
        [ [lng, lat],[lng, lat],[lng, lat] ]
        [ [lng, lat],[lng, lat],[lng, lat] ]
        [ [lng, lat],[lng, lat],[lng, lat] ]
      ]
      */
      function calculateBoundsFromNestedArrayOfArrays (array) {
        var x1 = null, x2 = null, y1 = null, y2 = null;

        for (var i = 0; i < array.length; i++) {
          var inner = array[i];

          for (var j = 0; j < inner.length; j++) {
            var innerinner = inner[j];
            for (var k = 0; k < innerinner.length; k++) {
              var lonlat = innerinner[k];

              var lon = lonlat[0];
              var lat = lonlat[1];

              if (x1 === null) {
                x1 = lon;
              } else if (lon < x1) {
                x1 = lon;
              }

              if (x2 === null) {
                x2 = lon;
              } else if (lon > x2) {
                x2 = lon;
              }

              if (y1 === null) {
                y1 = lat;
              } else if (lat < y1) {
                y1 = lat;
              }

              if (y2 === null) {
                y2 = lat;
              } else if (lat > y2) {
                y2 = lat;
              }
            }
          }
        }

        return [x1, y1, x2, y2];
      }

      /*
      Internal: Calculate a bounding box from an array of positions
      [
        [lng, lat],[lng, lat],[lng, lat]
      ]
      */
      function calculateBoundsFromArray (array) {
        var x1 = null, x2 = null, y1 = null, y2 = null;

        for (var i = 0; i < array.length; i++) {
          var lonlat = array[i];
          var lon = lonlat[0];
          var lat = lonlat[1];

          if (x1 === null) {
            x1 = lon;
          } else if (lon < x1) {
            x1 = lon;
          }

          if (x2 === null) {
            x2 = lon;
          } else if (lon > x2) {
            x2 = lon;
          }

          if (y1 === null) {
            y1 = lat;
          } else if (lat < y1) {
            y1 = lat;
          }

          if (y2 === null) {
            y2 = lat;
          } else if (lat > y2) {
            y2 = lat;
          }
        }

        return [x1, y1, x2, y2 ];
      }

      /*
      Internal: Calculate an bounding box for a feature collection
      */
      function calculateBoundsForFeatureCollection(featureCollection){
        var extents = [], extent;
        for (var i = featureCollection.features.length - 1; i >= 0; i--) {
          extent = calculateBounds(featureCollection.features[i].geometry);
          extents.push([extent[0],extent[1]]);
          extents.push([extent[2],extent[3]]);
        }

        return calculateBoundsFromArray(extents);
      }

      /*
      Internal: Calculate an bounding box for a geometry collection
      */
      function calculateBoundsForGeometryCollection(geometryCollection){
        var extents = [], extent;

        for (var i = geometryCollection.geometries.length - 1; i >= 0; i--) {
          extent = calculateBounds(geometryCollection.geometries[i]);
          extents.push([extent[0],extent[1]]);
          extents.push([extent[2],extent[3]]);
        }

        return calculateBoundsFromArray(extents);
      }

      function calculateEnvelope(geojson){
        var bounds = calculateBounds(geojson);
        return {
          x: bounds[0],
          y: bounds[1],
          w: Math.abs(bounds[0] - bounds[2]),
          h: Math.abs(bounds[1] - bounds[3])
        };
      }

      /*
      Internal: Convert radians to degrees. Used by spatial reference converters.
      */
      function radToDeg(rad) {
        return rad * DegreesPerRadian;
      }

      /*
      Internal: Convert degrees to radians. Used by spatial reference converters.
      */
      function degToRad(deg) {
        return deg * RadiansPerDegree;
      }

      /*
      Internal: Loop over each array in a geojson object and apply a function to it. Used by spatial reference converters.
      */
      function eachPosition(coordinates, func) {
        for (var i = 0; i < coordinates.length; i++) {
          // we found a number so lets convert this pair
          if(typeof coordinates[i][0] === "number"){
            coordinates[i] = func(coordinates[i]);
          }
          // we found an coordinates array it again and run THIS function against it
          if(typeof coordinates[i] === "object"){
            coordinates[i] = eachPosition(coordinates[i], func);
          }
        }
        return coordinates;
      }

      /*
      Public: Convert a GeoJSON Position object to Geographic (4326)
      */
      function positionToGeographic(position) {
        var x = position[0];
        var y = position[1];
        return [radToDeg(x / EarthRadius) - (Math.floor((radToDeg(x / EarthRadius) + 180) / 360) * 360), radToDeg((Math.PI / 2) - (2 * Math.atan(Math.exp(-1.0 * y / EarthRadius))))];
      }

      /*
      Public: Convert a GeoJSON Position object to Web Mercator (102100)
      */
      function positionToMercator(position) {
        var lng = position[0];
        var lat = Math.max(Math.min(position[1], 89.99999), -89.99999);
        return [degToRad(lng) * EarthRadius, EarthRadius/2.0 * Math.log( (1.0 + Math.sin(degToRad(lat))) / (1.0 - Math.sin(degToRad(lat))) )];
      }

      /*
      Public: Apply a function agaist all positions in a geojson object. Used by spatial reference converters.
      */
      function applyConverter(geojson, converter, noCrs){
        if(geojson.type === "Point") {
          geojson.coordinates = converter(geojson.coordinates);
        } else if(geojson.type === "Feature") {
          geojson.geometry = applyConverter(geojson.geometry, converter, true);
        } else if(geojson.type === "FeatureCollection") {
          for (var f = 0; f < geojson.features.length; f++) {
            geojson.features[f] = applyConverter(geojson.features[f], converter, true);
          }
        } else if(geojson.type === "GeometryCollection") {
          for (var g = 0; g < geojson.geometries.length; g++) {
            geojson.geometries[g] = applyConverter(geojson.geometries[g], converter, true);
          }
        } else {
          geojson.coordinates = eachPosition(geojson.coordinates, converter);
        }

        if(!noCrs){
          if(converter === positionToMercator){
            geojson.crs = MercatorCRS;
          }
        }

        if(converter === positionToGeographic){
          delete geojson.crs;
        }

        return geojson;
      }

      /*
      Public: Convert a GeoJSON object to ESRI Web Mercator (102100)
      */
      function toMercator(geojson) {
        return applyConverter(geojson, positionToMercator);
      }

      /*
      Convert a GeoJSON object to Geographic coordinates (WSG84, 4326)
      */
      function toGeographic(geojson) {
        return applyConverter(geojson, positionToGeographic);
      }


      /*
      Internal: -1,0,1 comparison function
      */
      function cmp(a, b) {
        if(a < b) {
          return -1;
        } else if(a > b) {
          return 1;
        } else {
          return 0;
        }
      }

      /*
      Internal: used for sorting
      */
      function compSort(p1, p2) {
        if (p1[0] > p2[0]) {
          return -1;
        } else if (p1[0] < p2[0]) {
          return 1;
        } else if (p1[1] > p2[1]) {
          return -1;
        } else if (p1[1] < p2[1]) {
          return 1;
        } else {
          return 0;
        }
      }


      /*
      Internal: used to determine turn
      */
      function turn(p, q, r) {
        // Returns -1, 0, 1 if p,q,r forms a right, straight, or left turn.
        return cmp((q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1]), 0);
      }

      /*
      Internal: used to determine euclidean distance between two points
      */
      function euclideanDistance(p, q) {
        // Returns the squared Euclidean distance between p and q.
        var dx = q[0] - p[0];
        var dy = q[1] - p[1];

        return dx * dx + dy * dy;
      }

      function nextHullPoint(points, p) {
        // Returns the next point on the convex hull in CCW from p.
        var q = p;
        for(var r in points) {
          var t = turn(p, q, points[r]);
          if(t === -1 || t === 0 && euclideanDistance(p, points[r]) > euclideanDistance(p, q)) {
            q = points[r];
          }
        }
        return q;
      }

      function convexHull(points) {
        // implementation of the Jarvis March algorithm
        // adapted from http://tixxit.wordpress.com/2009/12/09/jarvis-march/

        if(points.length === 0) {
          return [];
        } else if(points.length === 1) {
          return points;
        }

        // Returns the points on the convex hull of points in CCW order.
        var hull = [points.sort(compSort)[0]];

        for(var p = 0; p < hull.length; p++) {
          var q = nextHullPoint(points, hull[p]);

          if(q !== hull[0]) {
            hull.push(q);
          }
        }

        return hull;
      }

      function isConvex(points) {
        var ltz;

        for (var i = 0; i < points.length - 3; i++) {
          var p1 = points[i];
          var p2 = points[i + 1];
          var p3 = points[i + 2];
          var v = [p2[0] - p1[0], p2[1] - p1[1]];

          // p3.x * v.y - p3.y * v.x + v.x * p1.y - v.y * p1.x
          var res = p3[0] * v[1] - p3[1] * v[0] + v[0] * p1[1] - v[1] * p1[0];

          if (i === 0) {
            if (res < 0) {
              ltz = true;
            } else {
              ltz = false;
            }
          } else {
            if (ltz && (res > 0) || !ltz && (res < 0)) {
              return false;
            }
          }
        }

        return true;
      }

      function coordinatesContainPoint(coordinates, point) {
        var contains = false;
        for(var i = -1, l = coordinates.length, j = l - 1; ++i < l; j = i) {
          if (((coordinates[i][1] <= point[1] && point[1] < coordinates[j][1]) ||
               (coordinates[j][1] <= point[1] && point[1] < coordinates[i][1])) &&
              (point[0] < (coordinates[j][0] - coordinates[i][0]) * (point[1] - coordinates[i][1]) / (coordinates[j][1] - coordinates[i][1]) + coordinates[i][0])) {
            contains = !contains;
          }
        }
        return contains;
      }

      function polygonContainsPoint(polygon, point) {
        if (polygon && polygon.length) {
          if (polygon.length === 1) { // polygon with no holes
            return coordinatesContainPoint(polygon[0], point);
          } else { // polygon with holes
            if (coordinatesContainPoint(polygon[0], point)) {
              for (var i = 1; i < polygon.length; i++) {
                if (coordinatesContainPoint(polygon[i], point)) {
                  return false; // found in hole
                }
              }

              return true;
            } else {
              return false;
            }
          }
        } else {
          return false;
        }
      }

      function edgeIntersectsEdge(a1, a2, b1, b2) {
        var ua_t = (b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0]);
        var ub_t = (a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0]);
        var u_b  = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1]);

        if ( u_b !== 0 ) {
          var ua = ua_t / u_b;
          var ub = ub_t / u_b;

          if ( 0 <= ua && ua <= 1 && 0 <= ub && ub <= 1 ) {
            return true;
          }
        }

        return false;
      }

      function isNumber(n) {
        return !isNaN(parseFloat(n)) && isFinite(n);
      }

      function arraysIntersectArrays(a, b) {
        if (isNumber(a[0][0])) {
          if (isNumber(b[0][0])) {
            for (var i = 0; i < a.length - 1; i++) {
              for (var j = 0; j < b.length - 1; j++) {
                if (edgeIntersectsEdge(a[i], a[i + 1], b[j], b[j + 1])) {
                  return true;
                }
              }
            }
          } else {
            for (var k = 0; k < b.length; k++) {
              if (arraysIntersectArrays(a, b[k])) {
                return true;
              }
            }
          }
        } else {
          for (var l = 0; l < a.length; l++) {
            if (arraysIntersectArrays(a[l], b)) {
              return true;
            }
          }
        }
        return false;
      }

      /*
      Internal: Returns a copy of coordinates for s closed polygon
      */
      function closedPolygon(coordinates) {
        var outer = [ ];

        for (var i = 0; i < coordinates.length; i++) {
          var inner = coordinates[i].slice();
          if (pointsEqual(inner[0], inner[inner.length - 1]) === false) {
            inner.push(inner[0]);
          }

          outer.push(inner);
        }

        return outer;
      }

      function pointsEqual(a, b) {
        for (var i = 0; i < a.length; i++) {

          if (a[i] !== b[i]) {
            return false;
          }
        }

        return true;
      }

      function coordinatesEqual(a, b) {
        if (a.length !== b.length) {
          return false;
        }

        var na = a.slice().sort(compSort);
        var nb = b.slice().sort(compSort);

        for (var i = 0; i < na.length; i++) {
          if (na[i].length !== nb[i].length) {
            return false;
          }
          for (var j = 0; j < na.length; j++) {
            if (na[i][j] !== nb[i][j]) {
              return false;
            }
          }
        }

        return true;
      }

      /*
      Internal: An array of variables that will be excluded form JSON objects.
      */
      var excludeFromJSON = ["length"];

      /*
      Internal: Base GeoJSON Primitive
      */
      function Primitive(geojson){
        if(geojson){
          switch (geojson.type) {
          case 'Point':
            return new Point(geojson);

          case 'MultiPoint':
            return new MultiPoint(geojson);

          case 'LineString':
            return new LineString(geojson);

          case 'MultiLineString':
            return new MultiLineString(geojson);

          case 'Polygon':
            return new Polygon(geojson);

          case 'MultiPolygon':
            return new MultiPolygon(geojson);

          case 'Feature':
            return new Feature(geojson);

          case 'FeatureCollection':
            return new FeatureCollection(geojson);

          case 'GeometryCollection':
            return new GeometryCollection(geojson);

          default:
            throw new Error("Unknown type: " + geojson.type);
          }
        }
      }

      Primitive.prototype.toMercator = function(){
        return toMercator(this);
      };

      Primitive.prototype.toGeographic = function(){
        return toGeographic(this);
      };

      Primitive.prototype.envelope = function(){
        return calculateEnvelope(this);
      };

      Primitive.prototype.bbox = function(){
        return calculateBounds(this);
      };

      Primitive.prototype.convexHull = function(){
        var coordinates = [ ], i, j;
        if (this.type === 'Point') {
          return null;
        } else if (this.type === 'LineString' || this.type === 'MultiPoint') {
          if (this.coordinates && this.coordinates.length >= 3) {
            coordinates = this.coordinates;
          } else {
            return null;
          }
        } else if (this.type === 'Polygon' || this.type === 'MultiLineString') {
          if (this.coordinates && this.coordinates.length > 0) {
            for (i = 0; i < this.coordinates.length; i++) {
              coordinates = coordinates.concat(this.coordinates[i]);
            }
            if(coordinates.length < 3){
              return null;
            }
          } else {
            return null;
          }
        } else if (this.type === 'MultiPolygon') {
          if (this.coordinates && this.coordinates.length > 0) {
            for (i = 0; i < this.coordinates.length; i++) {
              for (j = 0; j < this.coordinates[i].length; j++) {
                coordinates = coordinates.concat(this.coordinates[i][j]);
              }
            }
            if(coordinates.length < 3){
              return null;
            }
          } else {
            return null;
          }
        } else if(this.type === "Feature"){
          var primitive = new Primitive(this.geometry);
          return primitive.convexHull();
        }

        return new Polygon({
          type: 'Polygon',
          coordinates: closedPolygon([convexHull(coordinates)])
        });
      };

      Primitive.prototype.toJSON = function(){
        var obj = {};
        for (var key in this) {
          if (this.hasOwnProperty(key) && excludeFromJSON.indexOf(key) === -1) {
            obj[key] = this[key];
          }
        }
        obj.bbox = calculateBounds(this);
        return obj;
      };

      Primitive.prototype.contains = function(primitive){
        return new Primitive(primitive).within(this);
      };

      Primitive.prototype.within = function(primitive) {
        var coordinates, i, contains;

        // if we are passed a feature, use the polygon inside instead
        if (primitive.type === 'Feature') {
          primitive = primitive.geometry;
        }

        // point.within(point) :: equality
        if (primitive.type === "Point") {
          if (this.type === "Point") {
            return pointsEqual(this.coordinates, primitive.coordinates);

          }
        }

        // point.within(multilinestring)
        if (primitive.type === "MultiLineString") {
          if (this.type === "Point") {
            for (i = 0; i < primitive.coordinates.length; i++) {
              var linestring = { type: "LineString", coordinates: primitive.coordinates[i] };

              if (this.within(linestring)) {
                return true;
              }
            }
          }
        }

        // point.within(linestring), point.within(multipoint)
        if (primitive.type === "LineString" || primitive.type === "MultiPoint") {
          if (this.type === "Point") {
            for (i = 0; i < primitive.coordinates.length; i++) {
              if (this.coordinates.length !== primitive.coordinates[i].length) {
                return false;
              }

              if (pointsEqual(this.coordinates, primitive.coordinates[i])) {
                return true;
              }
            }
          }
        }

        if (primitive.type === "Polygon") {
          // polygon.within(polygon)
          if (this.type === "Polygon") {
            // check for equal polygons
            if (primitive.coordinates.length === this.coordinates.length) {
              for (i = 0; i < this.coordinates.length; i++) {
                if (coordinatesEqual(this.coordinates[i], primitive.coordinates[i])) {
                  return true;
                }
              }
            }

            if (this.coordinates.length && polygonContainsPoint(primitive.coordinates, this.coordinates[0][0])) {
              return !arraysIntersectArrays(closedPolygon(this.coordinates), closedPolygon(primitive.coordinates));
            } else {
              return false;
            }

          // point.within(polygon)
          } else if (this.type === "Point") {
            return polygonContainsPoint(primitive.coordinates, this.coordinates);

          // linestring/multipoint withing polygon
          } else if (this.type === "LineString" || this.type === "MultiPoint") {
            if (!this.coordinates || this.coordinates.length === 0) {
              return false;
            }

            for (i = 0; i < this.coordinates.length; i++) {
              if (polygonContainsPoint(primitive.coordinates, this.coordinates[i]) === false) {
                return false;
              }
            }

            return true;

          // multilinestring.within(polygon)
          } else if (this.type === "MultiLineString") {
            for (i = 0; i < this.coordinates.length; i++) {
              var ls = new LineString(this.coordinates[i]);

              if (ls.within(primitive) === false) {
                contains++;
                return false;
              }
            }

            return true;

          // multipolygon.within(polygon)
          } else if (this.type === "MultiPolygon") {
            for (i = 0; i < this.coordinates.length; i++) {
              var p1 = new Primitive({ type: "Polygon", coordinates: this.coordinates[i] });

              if (p1.within(primitive) === false) {
                return false;
              }
            }

            return true;
          }

        }

        if (primitive.type === "MultiPolygon") {
          // point.within(multipolygon)
          if (this.type === "Point") {
            if (primitive.coordinates.length) {
              for (i = 0; i < primitive.coordinates.length; i++) {
                coordinates = primitive.coordinates[i];
                if (polygonContainsPoint(coordinates, this.coordinates) && arraysIntersectArrays([this.coordinates], primitive.coordinates) === false) {
                  return true;
                }
              }
            }

            return false;
          // polygon.within(multipolygon)
          } else if (this.type === "Polygon") {
            for (i = 0; i < this.coordinates.length; i++) {
              if (primitive.coordinates[i].length === this.coordinates.length) {
                for (j = 0; j < this.coordinates.length; j++) {
                  if (coordinatesEqual(this.coordinates[j], primitive.coordinates[i][j])) {
                    return true;
                  }
                }
              }
            }

            if (arraysIntersectArrays(this.coordinates, primitive.coordinates) === false) {
              if (primitive.coordinates.length) {
                for (i = 0; i < primitive.coordinates.length; i++) {
                  coordinates = primitive.coordinates[i];
                  if (polygonContainsPoint(coordinates, this.coordinates[0][0]) === false) {
                    contains = false;
                  } else {
                    contains = true;
                  }
                }

                return contains;
              }
            }

          // linestring.within(multipolygon), multipoint.within(multipolygon)
          } else if (this.type === "LineString" || this.type === "MultiPoint") {
            for (i = 0; i < primitive.coordinates.length; i++) {
              var p = { type: "Polygon", coordinates: primitive.coordinates[i] };

              if (this.within(p)) {
                return true;
              }

              return false;
            }

          // multilinestring.within(multipolygon)
          } else if (this.type === "MultiLineString") {
            for (i = 0; i < this.coordinates.length; i++) {
              var lines = new LineString(this.coordinates[i]);

              if (lines.within(primitive) === false) {
                return false;
              }
            }

            return true;

          // multipolygon.within(multipolygon)
          } else if (this.type === "MultiPolygon") {
            for (i = 0; i < primitive.coordinates.length; i++) {
              var mpoly = { type: "Polygon", coordinates: primitive.coordinates[i] };

              if (this.within(mpoly) === false) {
                return false;
              }
            }

            return true;
          }
        }

        // default to false
        return false;
      };

      Primitive.prototype.intersects = function(primitive) {
        // if we are passed a feature, use the polygon inside instead
        if (primitive.type === 'Feature') {
          primitive = primitive.geometry;
        }

        var p = new Primitive(primitive);
        if (this.within(primitive) || p.within(this)) {
          return true;
        }


        if (this.type !== 'Point' && this.type !== 'MultiPoint' &&
            primitive.type !== 'Point' && primitive.type !== 'MultiPoint') {
          return arraysIntersectArrays(this.coordinates, primitive.coordinates);
        } else if (this.type === 'Feature') {
          // in the case of a Feature, use the internal primitive for intersection
          var inner = new Primitive(this.geometry);
          return inner.intersects(primitive);
        }

        warn("Type " + this.type + " to " + primitive.type + " intersection is not supported by intersects");
        return false;
      };


      /*
      GeoJSON Point Class
        new Point();
        new Point(x,y,z,wtf);
        new Point([x,y,z,wtf]);
        new Point([x,y]);
        new Point({
          type: "Point",
          coordinates: [x,y]
        });
      */
      function Point(input){
        var args = Array.prototype.slice.call(arguments);

        if(input && input.type === "Point" && input.coordinates){
          extend(this, input);
        } else if(input && isArray(input)) {
          this.coordinates = input;
        } else if(args.length >= 2) {
          this.coordinates = args;
        } else {
          throw "Terraformer: invalid input for Terraformer.Point";
        }

        this.type = "Point";
      }

      Point.prototype = new Primitive();
      Point.prototype.constructor = Point;

      /*
      GeoJSON MultiPoint Class
          new MultiPoint();
          new MultiPoint([[x,y], [x1,y1]]);
          new MultiPoint({
            type: "MultiPoint",
            coordinates: [x,y]
          });
      */
      function MultiPoint(input){
        if(input && input.type === "MultiPoint" && input.coordinates){
          extend(this, input);
        } else if(isArray(input)) {
          this.coordinates = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.MultiPoint";
        }

        this.type = "MultiPoint";
      }

      MultiPoint.prototype = new Primitive();
      MultiPoint.prototype.constructor = MultiPoint;
      MultiPoint.prototype.forEach = function(func){
        for (var i = 0; i < this.coordinates.length; i++) {
          func.apply(this, [this.coordinates[i], i, this.coordinates]);
        }
        return this;
      };
      MultiPoint.prototype.addPoint = function(point){
        this.coordinates.push(point);
        return this;
      };
      MultiPoint.prototype.insertPoint = function(point, index){
        this.coordinates.splice(index, 0, point);
        return this;
      };
      MultiPoint.prototype.removePoint = function(remove){
        if(typeof remove === "number"){
          this.coordinates.splice(remove, 1);
        } else {
          this.coordinates.splice(this.coordinates.indexOf(remove), 1);
        }
        return this;
      };
      MultiPoint.prototype.get = function(i){
        return new Point(this.coordinates[i]);
      };

      /*
      GeoJSON LineString Class
          new LineString();
          new LineString([[x,y], [x1,y1]]);
          new LineString({
            type: "LineString",
            coordinates: [x,y]
          });
      */
      function LineString(input){
        if(input && input.type === "LineString" && input.coordinates){
          extend(this, input);
        } else if(isArray(input)) {
          this.coordinates = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.LineString";
        }

        this.type = "LineString";
      }

      LineString.prototype = new Primitive();
      LineString.prototype.constructor = LineString;
      LineString.prototype.addVertex = function(point){
        this.coordinates.push(point);
        return this;
      };
      LineString.prototype.insertVertex = function(point, index){
        this.coordinates.splice(index, 0, point);
        return this;
      };
      LineString.prototype.removeVertex = function(remove){
        this.coordinates.splice(remove, 1);
        return this;
      };

      /*
      GeoJSON MultiLineString Class
          new MultiLineString();
          new MultiLineString([ [[x,y], [x1,y1]], [[x2,y2], [x3,y3]] ]);
          new MultiLineString({
            type: "MultiLineString",
            coordinates: [ [[x,y], [x1,y1]], [[x2,y2], [x3,y3]] ]
          });
      */
      function MultiLineString(input){
        if(input && input.type === "MultiLineString" && input.coordinates){
          extend(this, input);
        } else if(isArray(input)) {
          this.coordinates = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.MultiLineString";
        }

        this.type = "MultiLineString";
      }

      MultiLineString.prototype = new Primitive();
      MultiLineString.prototype.constructor = MultiLineString;
      MultiLineString.prototype.forEach = function(func){
        for (var i = 0; i < this.coordinates.length; i++) {
          func.apply(this, [this.coordinates[i], i, this.coordinates ]);
        }
      };
      MultiLineString.prototype.get = function(i){
        return new LineString(this.coordinates[i]);
      };

      /*
      GeoJSON Polygon Class
          new Polygon();
          new Polygon([ [[x,y], [x1,y1], [x2,y2]] ]);
          new Polygon({
            type: "Polygon",
            coordinates: [ [[x,y], [x1,y1], [x2,y2]] ]
          });
      */
      function Polygon(input){
        if(input && input.type === "Polygon" && input.coordinates){
          extend(this, input);
        } else if(isArray(input)) {
          this.coordinates = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.Polygon";
        }

        this.type = "Polygon";
      }

      Polygon.prototype = new Primitive();
      Polygon.prototype.constructor = Polygon;
      Polygon.prototype.addVertex = function(point){
        this.insertVertex(point, this.coordinates[0].length - 1);
        return this;
      };
      Polygon.prototype.insertVertex = function(point, index){
        this.coordinates[0].splice(index, 0, point);
        return this;
      };
      Polygon.prototype.removeVertex = function(remove){
        this.coordinates[0].splice(remove, 1);
        return this;
      };
      Polygon.prototype.close = function() {
        this.coordinates = closedPolygon(this.coordinates);
      };
      Polygon.prototype.hasHoles = function() {
        return this.coordinates.length > 1;
      };
      Polygon.prototype.holes = function() {
        holes = [];
        if (this.hasHoles()) {
          for (var i = 1; i < this.coordinates.length; i++) {
            holes.push(new Polygon([this.coordinates[i]]));
          }
        }
        return holes;
      };

      /*
      GeoJSON MultiPolygon Class
          new MultiPolygon();
          new MultiPolygon([ [ [[x,y], [x1,y1]], [[x2,y2], [x3,y3]] ] ]);
          new MultiPolygon({
            type: "MultiPolygon",
            coordinates: [ [ [[x,y], [x1,y1]], [[x2,y2], [x3,y3]] ] ]
          });
      */
      function MultiPolygon(input){
        if(input && input.type === "MultiPolygon" && input.coordinates){
          extend(this, input);
        } else if(isArray(input)) {
          this.coordinates = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.MultiPolygon";
        }

        this.type = "MultiPolygon";
      }

      MultiPolygon.prototype = new Primitive();
      MultiPolygon.prototype.constructor = MultiPolygon;
      MultiPolygon.prototype.forEach = function(func){
        for (var i = 0; i < this.coordinates.length; i++) {
          func.apply(this, [this.coordinates[i], i, this.coordinates ]);
        }
      };
      MultiPolygon.prototype.get = function(i){
        return new Polygon(this.coordinates[i]);
      };
      MultiPolygon.prototype.close = function(){
        var outer = [];
        this.forEach(function(polygon){
          outer.push(closedPolygon(polygon));
        });
        this.coordinates = outer;
        return this;
      };

      /*
      GeoJSON Feature Class
          new Feature();
          new Feature({
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [ [ [[x,y], [x1,y1]], [[x2,y2], [x3,y3]] ] ]
            }
          });
          new Feature({
            type: "Polygon",
            coordinates: [ [ [[x,y], [x1,y1]], [[x2,y2], [x3,y3]] ] ]
          });
      */
      function Feature(input){
        if(input && input.type === "Feature"){
          extend(this, input);
        } else if(input && input.type && input.coordinates) {
          this.geometry = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.Feature";
        }

        this.type = "Feature";
      }

      Feature.prototype = new Primitive();
      Feature.prototype.constructor = Feature;

      /*
      GeoJSON FeatureCollection Class
          new FeatureCollection();
          new FeatureCollection([feature, feature1]);
          new FeatureCollection({
            type: "FeatureCollection",
            coordinates: [feature, feature1]
          });
      */
      function FeatureCollection(input){
        if(input && input.type === "FeatureCollection" && input.features){
          extend(this, input);
        } else if(isArray(input)) {
          this.features = input;
        } else {
          throw "Terraformer: invalid input for Terraformer.FeatureCollection";
        }

        this.type = "FeatureCollection";
      }

      FeatureCollection.prototype = new Primitive();
      FeatureCollection.prototype.constructor = FeatureCollection;
      FeatureCollection.prototype.forEach = function(func){
        for (var i = 0; i < this.features.length; i++) {
          func.apply(this, [this.features[i], i, this.features]);
        }
      };
      FeatureCollection.prototype.get = function(id){
        var found;
        this.forEach(function(feature){
          if(feature.id === id){
            found = feature;
          }
        });
        return new Feature(found);
      };

      /*
      GeoJSON GeometryCollection Class
          new GeometryCollection();
          new GeometryCollection([geometry, geometry1]);
          new GeometryCollection({
            type: "GeometryCollection",
            coordinates: [geometry, geometry1]
          });
      */
      function GeometryCollection(input){
        if(input && input.type === "GeometryCollection" && input.geometries){
          extend(this, input);
        } else if(isArray(input)) {
          this.geometries = input;
        } else if(input.coordinates && input.type){
          this.type = "GeometryCollection";
          this.geometries = [input];
        } else {
          throw "Terraformer: invalid input for Terraformer.GeometryCollection";
        }

        this.type = "GeometryCollection";
      }

      GeometryCollection.prototype = new Primitive();
      GeometryCollection.prototype.constructor = GeometryCollection;
      GeometryCollection.prototype.forEach = function(func){
        for (var i = 0; i < this.geometries.length; i++) {
          func.apply(this, [this.geometries[i], i, this.geometries]);
        }
      };
      GeometryCollection.prototype.get = function(i){
        return new Primitive(this.geometries[i]);
      };

      function createCircle(center, radius, interpolate){
        var mercatorPosition = positionToMercator(center);
        var steps = interpolate || 64;
        var polygon = {
          type: "Polygon",
          coordinates: [[]]
        };
        for(var i=1; i<=steps; i++) {
          var radians = i * (360/steps) * Math.PI / 180;
          polygon.coordinates[0].push([mercatorPosition[0] + radius * Math.cos(radians), mercatorPosition[1] + radius * Math.sin(radians)]);
        }
        polygon.coordinates = closedPolygon(polygon.coordinates);

        return toGeographic(polygon);
      }

      function Circle (center, radius, interpolate) {
        var steps = interpolate || 64;
        var rad = radius || 250;

        if(!center || center.length < 2 || !rad || !steps) {
          throw new Error("Terraformer: missing parameter for Terraformer.Circle");
        }

        extend(this, new Feature({
          type: "Feature",
          geometry: createCircle(center, rad, steps),
          properties: {
            radius: rad,
            center: center,
            steps: steps
          }
        }));
      }

      Circle.prototype = new Primitive();
      Circle.prototype.constructor = Circle;
      Circle.prototype.recalculate = function(){
        this.geometry = createCircle(this.properties.center, this.properties.radius, this.properties.steps);
        return this;
      };
      Circle.prototype.center = function(coordinates){
        if(coordinates){
          this.properties.center = coordinates;
          this.recalculate();
        }
        return this.properties.center;
      };
      Circle.prototype.radius = function(radius){
        if(radius){
          this.properties.radius = radius;
          this.recalculate();
        }
        return this.properties.radius;
      };
      Circle.prototype.steps = function(steps){
        if(steps){
          this.properties.steps = steps;
          this.recalculate();
        }
        return this.properties.steps;
      };

      Circle.prototype.toJSON = function() {
        var output = Primitive.prototype.toJSON.call(this);
        return output;
      };

      exports.Primitive = Primitive;
      exports.Point = Point;
      exports.MultiPoint = MultiPoint;
      exports.LineString = LineString;
      exports.MultiLineString = MultiLineString;
      exports.Polygon = Polygon;
      exports.MultiPolygon = MultiPolygon;
      exports.Feature = Feature;
      exports.FeatureCollection = FeatureCollection;
      exports.GeometryCollection = GeometryCollection;
      exports.Circle = Circle;

      exports.toMercator = toMercator;
      exports.toGeographic = toGeographic;

      exports.Tools = {};
      exports.Tools.positionToMercator = positionToMercator;
      exports.Tools.positionToGeographic = positionToGeographic;
      exports.Tools.applyConverter = applyConverter;
      exports.Tools.toMercator = toMercator;
      exports.Tools.toGeographic = toGeographic;
      exports.Tools.createCircle = createCircle;

      exports.Tools.calculateBounds = calculateBounds;
      exports.Tools.calculateEnvelope = calculateEnvelope;

      exports.Tools.coordinatesContainPoint = coordinatesContainPoint;
      exports.Tools.polygonContainsPoint = polygonContainsPoint;
      exports.Tools.arraysIntersectArrays = arraysIntersectArrays;
      exports.Tools.coordinatesContainPoint = coordinatesContainPoint;
      exports.Tools.coordinatesEqual = coordinatesEqual;
      exports.Tools.convexHull = convexHull;
      exports.Tools.isConvex = isConvex;

      exports.MercatorCRS = MercatorCRS;
      exports.GeographicCRS = GeographicCRS;

      return exports;
    }));
    });

    function toRadians(angleInDegrees) {
      return angleInDegrees * Math.PI / 180;
    }

    function toDegrees(angleInRadians) {
      return angleInRadians * 180 / Math.PI;
    }

    function offset(c1, distance, bearing) {
      var lat1 = toRadians(c1[1]);
      var lon1 = toRadians(c1[0]);
      var dByR = distance / 6378137; // distance divided by 6378137 (radius of the earth) wgs84
      var lat = Math.asin(
        Math.sin(lat1) * Math.cos(dByR) +
        Math.cos(lat1) * Math.sin(dByR) * Math.cos(bearing));
      var lon = lon1 + Math.atan2(
          Math.sin(bearing) * Math.sin(dByR) * Math.cos(lat1),
          Math.cos(dByR) - Math.sin(lat1) * Math.sin(lat));
      return [toDegrees(lon), toDegrees(lat)];
    }

    var circleToPolygon = function circleToPolygon(center, radius, numberOfSegments) {
      var n = numberOfSegments ? numberOfSegments : 32;
      var flatCoordinates = [];
      var coordinates = [];
      for (var i = 0; i < n; ++i) {
        flatCoordinates.push.apply(flatCoordinates, offset(center, radius, 2 * Math.PI * i / n));
      }
      flatCoordinates.push(flatCoordinates[0], flatCoordinates[1]);

      for (var i = 0, j = 0; j < flatCoordinates.length; j += 2) {
        coordinates[i++] = flatCoordinates.slice(j, j + 2);
      }

      return {
        type: 'Polygon',
        coordinates: [coordinates.reverse()]
      };
    };

    function getCircleMarkerRadius(circleMarker, crs, zoom) {
        var latLng = circleMarker.getLatLng();
        var point = crs.latLngToPoint(latLng, zoom);
        var delta = circleMarker.getRadius() / Math.SQRT2;
        var topLeftPoint = L.point([point.x - delta, point.y - delta]);
        var topLeftLatLng = crs.pointToLatLng(topLeftPoint, zoom);
        var radius = crs.distance(latLng, topLeftLatLng);
        return radius;
    }
    function circleToGeoJSONGeometry(latLng, radius) {
        // Terraformer result is incorrect, see https://github.com/Esri/terraformer/issues/321
        // return new Terraformer.Circle(L.GeoJSON.latLngToCoords(latLng), radius).geometry;
        return circleToPolygon(L.GeoJSON.latLngToCoords(latLng), radius);
    }
    function getLayersInPolygon(polygon, layers, options) {
        if (options === void 0) { options = {}; }
        var crs = options.crs || L.CRS.EPSG3857;
        var polygonGeometry = new terraformer.Primitive(polygon);
        var selectedLayers = layers.filter(function (layer) {
            var layerGeometry;
            if (layer instanceof L.Circle) {
                var latLng = layer.getLatLng();
                var radius = layer.getRadius();
                layerGeometry = circleToGeoJSONGeometry(latLng, radius);
            }
            else if (layer instanceof L.CircleMarker) {
                if (options.zoom != undefined) {
                    var latLng = layer.getLatLng();
                    var radius = getCircleMarkerRadius(layer, crs, options.zoom);
                    layerGeometry = circleToGeoJSONGeometry(latLng, radius);
                }
                else {
                    console.warn("Zoom is required for calculating CircleMarker polygon, falling back to center point only");
                    layerGeometry = layer.toGeoJSON().geometry;
                }
            }
            else if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                layerGeometry = layer.toGeoJSON().geometry;
            }
            else {
                return false;
            }
            return options.intersect && layerGeometry.type !== "Point" ?
                polygonGeometry.intersects(layerGeometry) :
                polygonGeometry.contains(layerGeometry);
        });
        return selectedLayers;
    }

    function styleInject(css, ref) {
      if ( ref === void 0 ) ref = {};
      var insertAt = ref.insertAt;

      if (!css || typeof document === 'undefined') { return; }

      var head = document.head || document.getElementsByTagName('head')[0];
      var style = document.createElement('style');
      style.type = 'text/css';

      if (insertAt === 'top') {
        if (head.firstChild) {
          head.insertBefore(style, head.firstChild);
        } else {
          head.appendChild(style);
        }
      } else {
        head.appendChild(style);
      }

      if (style.styleSheet) {
        style.styleSheet.cssText = css;
      } else {
        style.appendChild(document.createTextNode(css));
      }
    }

    var css = ".leaflet-lasso-active {\n    cursor: crosshair;\n    -webkit-user-select: none;\n       -moz-user-select: none;\n        -ms-user-select: none;\n            user-select: none;\n}\n\n.leaflet-lasso-active .leaflet-interactive {\n    cursor: crosshair;\n    pointer-events: none;\n}";
    styleInject(css);

    var ENABLED_EVENT = 'lasso.enabled';
    var DISABLED_EVENT = 'lasso.disabled';
    var FINISHED_EVENT = 'lasso.finished';
    var ACTIVE_CLASS = 'leaflet-lasso-active';
    var LassoHandler = /** @class */ (function (_super) {
        __extends(LassoHandler, _super);
        function LassoHandler(map, options) {
            if (options === void 0) { options = {}; }
            var _this = _super.call(this, map) || this;
            _this.options = {
                polygon: {
                    color: '#00C3FF',
                    weight: 2,
                },
                intersect: false,
            };
            _this.onDocumentMouseMoveBound = _this.onDocumentMouseMove.bind(_this);
            _this.onDocumentMouseUpBound = _this.onDocumentMouseUp.bind(_this);
            _this.map = map;
            L.Util.setOptions(_this, options);
            return _this;
        }
        LassoHandler.prototype.setOptions = function (options) {
            this.options = __assign({}, this.options, options);
        };
        LassoHandler.prototype.toggle = function () {
            if (this.enabled()) {
                this.disable();
            }
            else {
                this.enable();
            }
        };
        LassoHandler.prototype.addHooks = function () {
            this.map.getPane('mapPane');
            this.map.on('mousedown', this.onMapMouseDown, this);
            var mapContainer = this.map.getContainer();
            mapContainer.classList.add(ACTIVE_CLASS);
            this.map.dragging.disable();
            this.map.fire(ENABLED_EVENT);
        };
        LassoHandler.prototype.removeHooks = function () {
            if (this.polygon) {
                this.map.removeLayer(this.polygon);
                this.polygon = undefined;
            }
            this.map.off('mousedown', this.onMapMouseDown, this);
            document.removeEventListener('mousemove', this.onDocumentMouseMoveBound);
            document.removeEventListener('mouseup', this.onDocumentMouseUpBound);
            this.map.getContainer().classList.remove(ACTIVE_CLASS);
            document.body.classList.remove(ACTIVE_CLASS);
            this.map.dragging.enable();
            this.map.fire(DISABLED_EVENT);
        };
        LassoHandler.prototype.getPolygon = function () {
            return this.polygon;
        };
        LassoHandler.prototype.onMapMouseDown = function (event) {
            var event2 = event;
            // activate lasso only for left mouse button click
            if (event2.originalEvent.buttons !== 1) {
                this.disable();
                return;
            }
            // skip clicks on controls
            if (event2.originalEvent.target.closest('.leaflet-control-container')) {
                return;
            }
            this.polygon = new LassoPolygon([event2.latlng], this.options.polygon).addTo(this.map);
            document.body.classList.add(ACTIVE_CLASS);
            document.addEventListener('mousemove', this.onDocumentMouseMoveBound);
            document.addEventListener('mouseup', this.onDocumentMouseUpBound);
        };
        LassoHandler.prototype.onDocumentMouseMove = function (event) {
            if (!this.polygon) {
                return;
            }
            var event2 = event;
            // keep lasso active only if left mouse button is hold
            if (event2.buttons !== 1) {
                console.warn('mouseup event was missed');
                this.finish();
                return;
            }
            this.polygon.addLatLng(this.map.mouseEventToLatLng(event2));
        };
        LassoHandler.prototype.onDocumentMouseUp = function () {
            this.finish();
        };
        LassoHandler.prototype.finish = function () {
            var _this = this;
            if (!this.polygon) {
                return;
            }
            var polygon = this.polygon.toGeoJSON().geometry;
            var layers = [];
            this.map.eachLayer(function (layer) {
                if (layer === _this.polygon || layer === _this.polygon.polyline || layer === _this.polygon.polygon) {
                    return;
                }
                if (layer instanceof L.Marker || layer instanceof L.Path) {
                    layers.push(layer);
                }
                else if (L.MarkerCluster && layer instanceof L.MarkerCluster) {
                    layers.push.apply(layers, layer.getAllChildMarkers());
                }
            });
            var selectedFeatures = getLayersInPolygon(polygon, layers, {
                zoom: this.map.getZoom(),
                crs: this.map.options.crs,
                intersect: this.options.intersect,
            });
            this.map.fire(FINISHED_EVENT, {
                latLngs: this.polygon.getLatLngs(),
                layers: selectedFeatures,
            });
            this.disable();
        };
        return LassoHandler;
    }(L.Handler));

    var css$1 = ".leaflet-control-lasso {\n    background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsSAAALEgHS3X78AAAD6UlEQVR4nO1b7XHbMAwFfP0fdYKqE8QbRJ0gGUEjaAR3A4/gbuBOUHWCKhs4E1SegD06jzmYpWhJpiRKNu58Tix+AA8gCQIQK6Xolml109LfAbgDcAfg5gH4NPQEzJwSkf4kRLR2NKmJqNLfSqlqaH7+4y/0McjML0SUQdinHkO8ApCSiPZKqToogxYFAQBC50T03NDkN74raFzSGtahreSLo+9PALG7mlEXaQD6fMD0BgIp8TkQ0ZaINChpl7ExZoZxK2vcGr8nfXl2ztm5g1twI/Q6KHPvVlFg/DMgJgEAWpWCay3lIYX2zJ1bQFQhAO+i9b2l8VEEd/BSWEooBgUAm5REPvg67AGCrZDdIABgQ6qF1oOu8QBAbK4FwTd4bq23SbXeks/OIPg0f7V5TQRCpz3BNdhamH30wgu+CwFC66VqD5IIByRas/eAYDbGqi8AW+FszEp4ocC6y1KQneW6z+YmvJDDLIVDVwBKdNzPVXghi/FbLjprp4AIM2fi6loMcusal8zN8eXirOp885jNrn/BAlKxnL17GWPj+As8viqlDguwAG3V+hR7JKJvSqmyqd1KmMnrUoQHGaEzX6OVaLAfg6sRyUSeUt+UKxGobDSTmZKR5yIAj/h79IhsDPSRFxg6+ho9AAukpI1IgydGxiY4dSRON+/SXgwAyE1sHbkF79JmeEuaPs91H4DWf+Ffk1nSgDwQ0RH5iUbZqgXcAI0MG/FbKn7f+i5DZo14PabISR/lb0qpjWETXq252LmSsidaCYfh8s0pbnKZuFHuEzNvmNl5MiR9YmmRLYHaxb8VJ3SG+UzD3ZyvwyI/UEPozMoZFE2xTjOADId1yuhGBMLO0raSUSE74HsGgDoPiZULsIISPkFqtUlEuOx0YsiHadeIakTC57bGPW0zAVRiP+yVXJhY+M6JHLFcCtfDvUAoahCseoXW0Wz0Oy1310O5WUQLgmX2ZddEzkffhoc2CJMUQ3h4kzt+v7S4ke/CRKWYaBtBYURmF2tcMda7bC0absWEk5TG4ISyS3Suury1BqAB+XIMIDCv7eAEsUTvHtDQoak8bhPSexSlcXadYBlqHu8p0BMIZRVIti9QeD/Hc/S1hVawgKDuufQDriqVZeYcAjeVyL4BGBc1lcaSKY8dolaYmTXgf0ykKFStcCIKpM33Q8vuR1EcXeEuMkhoDnyWCKB81wGUQV+aEhFaJ/mSlgPwYvyHZ8QN9SlS38RbY3hnYQ/NHyH8KVq0+DdGdCgMS+sRe1ImX8xYvAUw8wGb7Q9c88/2l1sAIEPBlPM0ur85GgEPk9IdgAh4mJTuAETAw3RERP8Ab2Uzgrad13wAAAAASUVORK5CYII=');\n    background-size: 22px;\n}";
    styleInject(css$1);

    var LassoControl = /** @class */ (function (_super) {
        __extends(LassoControl, _super);
        function LassoControl(options) {
            if (options === void 0) { options = {}; }
            var _this = _super.call(this) || this;
            _this.options = {
                position: 'topright',
            };
            L.Util.setOptions(_this, options);
            return _this;
        }
        LassoControl.prototype.setOptions = function (options) {
            this.options = __assign({}, this.options, options);
            if (this.lasso) {
                this.lasso.setOptions(this.options);
            }
        };
        LassoControl.prototype.onAdd = function (map) {
            this.lasso = new LassoHandler(map, this.options);
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            var button = L.DomUtil.create('a', 'leaflet-control-lasso', container);
            button.href = '#';
            button.title = 'Toggle Lasso';
            button.setAttribute('role', 'button');
            button.setAttribute('aria-label', button.title);
            L.DomEvent.addListener(button, 'click', this.toggle, this);
            return container;
        };
        LassoControl.prototype.enabled = function () {
            if (!this.lasso) {
                return false;
            }
            return this.lasso.enabled();
        };
        LassoControl.prototype.enable = function () {
            if (!this.lasso) {
                return;
            }
            this.lasso.enable();
        };
        LassoControl.prototype.disable = function () {
            if (!this.lasso) {
                return;
            }
            this.lasso.disable();
        };
        LassoControl.prototype.toggle = function () {
            if (!this.lasso) {
                return;
            }
            this.lasso.toggle();
        };
        return LassoControl;
    }(L.Control));

    L.Lasso = LassoHandler;
    L.lasso = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return new (LassoHandler.bind.apply(LassoHandler, [void 0].concat(args)))();
    };
    L.Control.Lasso = LassoControl;
    L.control.lasso = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return new (LassoControl.bind.apply(LassoControl, [void 0].concat(args)))();
    };

    exports.ACTIVE_CLASS = ACTIVE_CLASS;
    exports.DISABLED_EVENT = DISABLED_EVENT;
    exports.ENABLED_EVENT = ENABLED_EVENT;
    exports.FINISHED_EVENT = FINISHED_EVENT;
    exports.LassoControl = LassoControl;
    exports.LassoHandler = LassoHandler;

    Object.defineProperty(exports, '__esModule', { value: true });

}));
//# sourceMappingURL=leaflet-lasso.umd.js.map