# Nombres:
- Sergio Steven Parra Cuesta
- Diego Alejandro Arismendi Guzmán
- Laura Alejandra Rincon Hernandez
- Cristian Andrés Cardenas Muñoz

// Aplicación de inventario

db.createCollection("productos", {
	validator: {
		$jsonSchema: {
			bsonType: "object",
			description: "Productos",
			required: ["nombre", "categoria", "proveedor", "precio", "stock"],
			additionalProperties: true,
			minProperties: 8,
			maxProperties: 12,
			properties: {
				_id: {
                    bsonType: "objectId",
                    description: "Identificador del producto"
				},
				nombre: {
					bsonType: "string",
					description: "Nombre del producto"
				},
				categoria: {
					bsonType: "object",
                    description: "Categoria",
					required: ["nombre"],
					additionalProperties: false,
                    minProperties: 1,
                    maxProperties: 2,
					properties: {
						nombre: {
							bsonType: "string",
							description: "Nombre de la categoria"
						},
						descripcion: {
							bsonType: "string",
							description: "Descripcion opcional de la categoria"
						}
					}
				},
				proveedor: {
					bsonType: "object",
                    description: "Proveedor",
					required: ["nombre", "contacto", "telefono"],
					additionalProperties: true,
                    minProperties: 5,
                    maxProperties: 10,
					properties: {
						razonSocial: {
							bsonType: "string",
							description: "Nombre del proveedor"
						},
						contacto: {
							bsonType: "string",
							description: "Persona de contacto"
						},
						telefono: {
							bsonType: "string",
							description: "Telefono"
						},
						email: {
							bsonType: "string",
							pattern: "^.+@.+\\..+$",
							description: "Correo electronico"
						},
						direccion: {
							bsonType: "string",
							description: "Direccion"
						}
					}
				},
				descripcion: {
					bsonType: "string",
					description: "Descripcion opcional del producto"
				},
				precio: {
					bsonType: "double",
					minimum: 0,
					description: "Precio unitario"
				},
				stock: {
					bsonType: "int",
					minimum: 0,
                    maximum: 200,
					description: "Cantidad disponible en stock"
				},
				img: {
					bsonType: "string",
					description: "Ruta o nombre de la imagen"
				}
			}
		}
	}
})

// Mascotas
db.createCollection("mascotas", {
	validator: {
		$jsonSchema: {
            bsonType: "object",
            required: ["nombre", "telefono", "mascotas"],
            description: "Datos del dueño de la mascota",
            additionalProperties: true,
            minProperties: 2,
            maxProperties: 7,
            properties: {
                nombre: {
					bsonType: "string",
					description: "Nombre del dueño"
                },
                telefono: {
                    bsonType: "string",
                    description: "Contacto",
                },
                direccion: {
                    bsonType: "string",
                    description: "Dirección"
                },
                email: {
                    bsonType: "string",
                    description: "Correo",
                    pattern: "^.+@.+\\..+$"
                }, 
                mascotas: {
                    bsonType: "array",
                    description: "Mascotas",
                    items: {
                        bsonType: "object",
                        required: ["nombre", "especie", "raza", "edad", "vacunado"],
                        additionalProperties: false,
                        minProperties: 6,
                        maxProperties: 9,
                        properties: {
                            nombre: {
                                bsonType: "string",
                                description: "Nombre"
                            },
                            especie: {
                                bsonType: "string",
                                description: "Especie animal"
                            },
                            raza: {
                                bsonType: "string",
                                description: "Raza animal",
                            },
                            edad: {
                                bsonType: "int",
                                description: "Edad",
                                minimum: 0,
                                maximum: 50
                            },
                            fecha_nacimiento: {
								bsonType: "date",
								description: "Fecha de nacimiento"
                            },
                            peso: {
                                bsonType: "double",
                                minimum: 0,
                                maximum: 100,
								description: "Peso de la mascota"
                            },
                            vacunado: {
								bsonType: "bool",
								description: "Estado de vacunacion"
                            },
                            historialMedico : {
                                bsonType: "array",
                                description: "Historiales medicos",
                                items: {
                                    bsonType: "object",
                                    required: ["fecha_visita", "motivo_visita", "diagnostico", "tratamiento"],
                                    additionalProperties: false,
                                    minProperties: 5,
                                    maxProperties: 7,
                                    properties: {
                                        _id: {
                                            bsonType: "objectId",
                                            description: "Identificador del historial medico"
                                        },
                                        alergias: {
                                            bsonType: "string",
                                            description: "Alergias registradas"
                                        },
                                        fecha_visita: {
                                            bsonType: "date",
                                            description: "Fecha de visita"
                                        },
                                        motivo_visita: {
                                            bsonType: "string",
                                            description: "Motivo de la visita"
                                        },
                                        diagnostico: {
                                            bsonType: "string",
                                            description: "Diagnostico medico"
                                        },
                                        tratamiento: {
                                            bsonType: "string",
                                            description: "Tratamiento indicado"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                citas: {
                    bsonType: "array",
                    description: "Citas",
                    items: {
                        bsonType: "object",
                        required: ["fecha", "motivo", "veterinario", "estado"],
                        additionalProperties: false,
                        minProperties: 5,
                        maxProperties: 6,
                        properties: {
                            _id: {
								bsonType: "objectId",
								description: "Identificador de la cita"
                            },
                            fecha: {
								bsonType: "date",
								description: "Fecha y hora de la cita"
                            },
                            motivo: {
								bsonType: "string",
								description: "Motivo de la cita"
                            },
                            veterinario: {
								bsonType: "string",
								description: "Veterinario asignado"
                            },
                            estado: {
                                bsonType: "string",
                                enum: ["Pendiente", "Confirmada", "Cancelada"],
								description: "Estado de la cita"
                            }
                        }
                    }
                },
                vacunas : {
                    bsonType: "array",
                    description: "Vacunas",
                    items: {
                        bsonType: "object",
                        required: ["nombre_vacuna", "fecha_aplicacion", "veterinario"],
                        additionalProperties: false,
                        minProperties: 4,
                        maxProperties: 5,
                        properties: {
                            _id: {
								bsonType: "objectId",
								description: "Identificador de la vacuna"
                            },
                            nombre_vacuna: {
								bsonType: "string",
								description: "Nombre de la vacuna"
                            },
                            fecha_aplicacion: {
								bsonType: "date",
								description: "Fecha de aplicacion"
                            },
                            veterinario: {
								bsonType: "string",
								description: "Veterinario que aplica la vacuna"
                            }
                        }
                    }
                }
            }
        }
    }
})

// Facturación
db.createCollection("facturas", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            description: "Facturas",
            required: ["fecha", "subtotal", "iva", "total", "estado", "detalles"],
            additionalProperties: false,
            minProperties: 6,
            maxProperties: 9,
            properties: {
                _id: {
                    bsonType: "objectId",
                    description: "Identificador de la factura"
                },
                cliente: {
                    bsonType: "object",
                    description: "Cliente de la factura",
                    required: ["_id", "nombre"],
                    additionalProperties: false,
                    minProperties: 2,
                    maxProperties: 2,
                    properties: {
                        _id: {
                            bsonType: "objectId",
                            description: "Identificador del cliente"
                        },
                        nombre: {
                            bsonType: "string",
                            description: "Nombre del cliente"
                        }
                    }
                },
                mascota: {
                    bsonType: "object",
                    description: "Mascota asociada a la factura",
                    required: ["_id", "nombre"],
                    additionalProperties: false,
                    minProperties: 2,
                    maxProperties: 2,
                    properties: {
                        _id: {
                            bsonType: "objectId",
                            description: "Identificador de la mascota"
                        },
                        nombre: {
                            bsonType: "string",
                            description: "Nombre de la mascota"
                        }
                    }
                },
                fecha: {
                    bsonType: "date",
                    description: "Fecha de la factura"
                },
                subtotal: {
                    bsonType: "double",
                    minimum: 0,
                    description: "Subtotal de la factura"
                },
                iva: {
                    bsonType: "double",
                    minimum: 0,
                    description: "Impuesto IVA"
                },
                total: {
                    bsonType: "double",
                    minimum: 0,
                    description: "Total de la factura"
                },
                estado: {
                    bsonType: "string",
                    enum: ["BORRADOR", "PENDIENTE", "PAGADA", "CANCELADA"],
                    description: "Estado de la factura"
                },
                detalles: {
                    bsonType: "array",
                    description: "Detalle de conceptos facturados",
                    items: {
                        bsonType: "object",
                        required: ["tipo", "descripcion", "cantidad", "precio_unitario", "subtotal"],
                        additionalProperties: false,
                        minProperties: 5,
                        maxProperties: 8,
                        properties: {
                            _id: {
                                bsonType: "objectId",
                                description: "Identificador del detalle"
                            },
                            tipo: {
                                bsonType: "string",
                                enum: ["CITA", "PRODUCTO", "OTRO"],
                                description: "Tipo de detalle"
                            },
                            cita: {
                                bsonType: "object",
                                description: "Cita asociada",
                                required: ["_id"],
                                additionalProperties: false,
                                minProperties: 1,
                                maxProperties: 1,
                                properties: {
                                    _id: {
                                        bsonType: "objectId",
                                        description: "Identificador de la cita"
                                    }
                                }
                            },
                            producto: {
                                bsonType: "object",
                                description: "Producto asociado",
                                required: ["_id"],
                                additionalProperties: false,
                                minProperties: 1,
                                maxProperties: 1,
                                properties: {
                                    _id: {
                                        bsonType: "objectId",
                                        description: "Identificador del producto"
                                    }
                                }
                            },
                            descripcion: {
                                bsonType: "string",
                                description: "Descripcion del detalle"
                            },
                            cantidad: {
                                bsonType: "int",
                                minimum: 1,
                                maximum: 1000,
                                description: "Cantidad"
                            },
                            precio_unitario: {
                                bsonType: "double",
                                minimum: 0,
                                description: "Precio unitario"
                            },
                            subtotal: {
                                bsonType: "double",
                                minimum: 0,
                                description: "Subtotal del detalle"
                            }
                        }
                    }
                }
            }
        }
    }
})

// Usuarios

db.createCollection("usuarios", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            description: "Usuarios del aplicativo",
            required: ["nombre", "apellido", "tipo_documento", "numero_documento", "correo", "telefono", "direccion", "cuenta"],
            additionalProperties: false,
            minProperties: 8,
            maxProperties: 10,
            properties: {
                _id: {
                    bsonType: "objectId",
                    description: "Identificador del usuario"
                },
                nombre: {
                    bsonType: "string",
                    description: "Nombre del usuario"
                },
                apellido: {
                    bsonType: "string",
                    description: "Apellido del usuario"
                },
                tipo_documento: {
                    bsonType: "string",
                    enum: ["CC", "TI", "CE", "Otro"],
                    description: "Tipo de documento"
                },
                numero_documento: {
                    bsonType: "string",
                    description: "Numero de documento"
                },
                correo: {
                    bsonType: "string",
                    pattern: "^.+@.+\\..+$",
                    description: "Correo del usuario"
                },
                telefono: {
                    bsonType: "string",
                    description: "Telefono del usuario"
                },
                direccion: {
                    bsonType: "string",
                    description: "Direccion del usuario"
                },
                cuenta: {
                    bsonType: "object",
                    description: "Cuenta del usuario",
                    required: ["contrasena", "estado"],
                    additionalProperties: false,
                    minProperties: 3,
                    maxProperties: 3,
                    properties: {
                        _id: {
                            bsonType: "objectId",
                            description: "Identificador de la cuenta"
                        },
                        contrasena: {
                            bsonType: "string",
                            description: "Contrasena"
                        },
                        estado: {
                            bsonType: "bool",
                            description: "Activo o inactivo"
                        }
                    }
                }
            }
        }
    }
})

// Contacto
db.createCollection("contactos", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            description: "Contactos del aplicativo",
            required: ["nombre", "numero_contacto", "email", "mensaje"],
            additionalProperties: false,
            minProperties: 4,
            maxProperties: 5,
            properties: {
                _id: {
                    bsonType: "objectId",
                    description: "Identificador del contacto"
                },
                nombre: {
                    bsonType: "string",
                    description: "Nombre de la persona de contacto"
                },
                numero_contacto: {
                    bsonType: "string",
                    description: "Numero de contacto"
                },
                email: {
                    bsonType: "string",
                    pattern: "^.+@.+\\..+$",
                    description: "Correo electronico"
                },
                mensaje: {
                    bsonType: "string",
                    description: "Mensaje enviado"
                }
            }
        }
    }
})