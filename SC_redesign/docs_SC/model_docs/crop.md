## __Crop__
*Under construction*

### __Crop data__

The growth cycle of a crop is controlled by attributes contained in the `CropData` data class. `CropData` 
stores and updates all the crop variables needed to configure and initialize the processes involved when
a crop grows in a field. 

Differences in growth between crops are also defined by the parameters contained in `CropData`. The class
holds default values for a generic crop as well as specific crop data classes (*e.g.*, `CornData` class) with 
its values set to different defaults.

The **crops supported by RUFAS** at present with available crop data classes within `CropData` are: 

- Corn (*Zea mays*)
- Spring wheat (*Triticum aestivum*)
- Winter wheat (*Triticum aestivum*)
- Cereal rye (*Secale cereale*)
- Spring barley (*Hordeum vulgare*)
- Fall oats (*Avena sativa*)
- Tall fescue (*Festuca arundinacea*)
- Alfalfa (*Medicago sativa*)
- Soybean (*Glycine max*)
- Sugar beet (*Beta vulgaris var. saccharifera*)
- Potato (*Solanum tuberosum*)
- Triticale (*x Triticosecale*)

---
**References**: for more information visit [Sphinx][1] documentation (TBA). 

[1]:https://www.sphinx-doc.org/en/master/